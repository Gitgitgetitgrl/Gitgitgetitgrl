/**
 * KDP Master Automation — Google Apps Script (Part 2)
 *
 * Consolidated features:
 *   - LISTS-driven named ranges + dropdown refresh across metadata tabs
 *   - ERROR_LOG logging with daily archived retention (ERROR_LOG_ARCHIVE)
 *   - Critical email alerts with a mail-quota check before sending
 *   - Checkpoint-based continuation using PropertiesService (safe batch resume)
 *   - Watchdog monitoring + job reset tools
 *   - Built-in test harness runUnitTests() for pure/helper logic
 *
 * Install: Extensions -> Apps Script, paste this file, save, run onOpen once
 * (authorize when prompted), then use the "KDP Automation" menu.
 */

// ---- Config ---------------------------------------------------------------
var CFG = {
  TABS: {
    DRAFT: 'META_DRAFT',
    APPROVED: 'META_APPROVED',
    LISTS: 'LISTS',
    CHANGELOG: 'CHANGELOG',
    ARCHIVE: 'ARCHIVE',
    ERROR_LOG: 'ERROR_LOG',
    ERROR_LOG_ARCHIVE: 'ERROR_LOG_ARCHIVE'
  },
  // Columns in metadata tabs that are constrained by a LISTS list_name.
  DROPDOWN_COLUMNS: {
    trim_size: 'trim_size',
    bleed: 'bleed',
    paper_type: 'paper_type',
    approval_status: 'approval_status'
  },
  ALERT_EMAIL: '',                 // set to receive critical alerts
  MIN_MAIL_QUOTA: 5,               // don't send if remaining quota is below this
  ERROR_LOG_RETENTION_DAYS: 30
};

// ---- Menu -----------------------------------------------------------------
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('KDP Automation')
    .addItem('Refresh dropdowns', 'refreshDropdowns')
    .addItem('Archive old error logs', 'archiveErrorLogs')
    .addSeparator()
    .addItem('Reset stuck job', 'resetJob')
    .addItem('Run self-tests', 'runUnitTests')
    .addToUi();
}

// ---- Pure helpers (unit-tested; no Sheet/Mail access) ---------------------

/** Group LISTS rows [[list_name, value], ...] into { list_name: [values] }. */
function buildListMap(rows) {
  var map = {};
  for (var i = 0; i < rows.length; i++) {
    var name = String(rows[i][0]).trim();
    var value = String(rows[i][1]).trim();
    if (!name || name === 'list_name') continue;
    if (!map[name]) map[name] = [];
    if (value) map[name].push(value);
  }
  return map;
}

/** Column letter (1 -> A, 27 -> AA) for building A1 ranges. */
function colToLetter(col) {
  var s = '';
  while (col > 0) {
    var m = (col - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    col = Math.floor((col - 1) / 26);
  }
  return s;
}

/** Index (1-based) of a header in a header row, or -1. */
function headerIndex(headers, name) {
  for (var i = 0; i < headers.length; i++) {
    if (String(headers[i]).trim() === name) return i + 1;
  }
  return -1;
}

/** True if a date string is older than retentionDays from `now`. */
function isExpired(dateStr, now, retentionDays) {
  var t = new Date(dateStr).getTime();
  if (isNaN(t)) return false;
  var ageDays = (now.getTime() - t) / (1000 * 60 * 60 * 24);
  return ageDays > retentionDays;
}

// ---- Sheet operations -----------------------------------------------------

function sheet_(name) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

/** Rebuild data-validation dropdowns on metadata tabs from the LISTS tab. */
function refreshDropdowns() {
  try {
    var lists = sheet_(CFG.TABS.LISTS).getDataRange().getValues();
    var map = buildListMap(lists);
    [CFG.TABS.DRAFT, CFG.TABS.APPROVED].forEach(function (tabName) {
      var sh = sheet_(tabName);
      var headers = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
      var lastRow = Math.max(sh.getMaxRows(), 2);
      Object.keys(CFG.DROPDOWN_COLUMNS).forEach(function (col) {
        var listName = CFG.DROPDOWN_COLUMNS[col];
        var values = map[listName];
        var idx = headerIndex(headers, col);
        if (!values || idx < 0) return;
        var rule = SpreadsheetApp.newDataValidation()
          .requireValueInList(values, true).setAllowInvalid(false).build();
        sh.getRange(2, idx, lastRow - 1, 1).setDataValidation(rule);
      });
    });
    logInfo('refreshDropdowns', 'dropdowns refreshed');
  } catch (e) {
    logError('refreshDropdowns', e);
  }
}

// ---- Error log + retention ------------------------------------------------

function logInfo(where, msg) { writeLog_('INFO', where, msg); }

function logError(where, err) {
  var msg = (err && err.stack) ? err.stack : String(err);
  writeLog_('ERROR', where, msg);
  sendCriticalAlert('KDP ERROR: ' + where, msg);
}

function writeLog_(level, where, msg) {
  var sh = sheet_(CFG.TABS.ERROR_LOG);
  if (sh.getLastRow() === 0) {
    sh.appendRow(['timestamp', 'level', 'where', 'message']);
  }
  sh.appendRow([new Date().toISOString(), level, where, msg]);
}

/** Move ERROR_LOG rows older than retention into ERROR_LOG_ARCHIVE. */
function archiveErrorLogs() {
  var sh = sheet_(CFG.TABS.ERROR_LOG);
  var data = sh.getDataRange().getValues();
  if (data.length <= 1) return;
  var header = data[0];
  var now = new Date();
  var keep = [header], move = [];
  for (var i = 1; i < data.length; i++) {
    if (isExpired(data[i][0], now, CFG.ERROR_LOG_RETENTION_DAYS)) move.push(data[i]);
    else keep.push(data[i]);
  }
  if (move.length === 0) return;
  var arch = sheet_(CFG.TABS.ERROR_LOG_ARCHIVE);
  if (arch.getLastRow() === 0) arch.appendRow(header);
  move.forEach(function (r) { arch.appendRow(r); });
  sh.clearContents();
  sh.getRange(1, 1, keep.length, header.length).setValues(keep);
  logInfo('archiveErrorLogs', 'archived ' + move.length + ' rows');
}

// ---- Email alerts with quota check ---------------------------------------

function sendCriticalAlert(subject, body) {
  if (!CFG.ALERT_EMAIL) return;                       // not configured -> skip
  var remaining = MailApp.getRemainingDailyQuota();
  if (remaining < CFG.MIN_MAIL_QUOTA) {
    writeLog_('WARN', 'sendCriticalAlert',
      'skipped alert; mail quota low (' + remaining + ')');
    return;
  }
  MailApp.sendEmail(CFG.ALERT_EMAIL, subject, body);
}

// ---- Checkpoint continuation + watchdog ----------------------------------

var CHECKPOINT_KEY = 'kdp_checkpoint';

/** Process rows in safe batches, resuming from the last checkpoint. */
function processApprovedInBatches(batchSize) {
  batchSize = batchSize || 25;
  var props = PropertiesService.getScriptProperties();
  var start = parseInt(props.getProperty(CHECKPOINT_KEY) || '2', 10); // skip header
  var sh = sheet_(CFG.TABS.APPROVED);
  var last = sh.getLastRow();
  var end = Math.min(start + batchSize - 1, last);
  if (start > last) { props.deleteProperty(CHECKPOINT_KEY); return; }

  try {
    // ... per-row work would go here (e.g., stage upload prep) ...
    props.setProperty(CHECKPOINT_KEY, String(end + 1));
    props.setProperty('kdp_watchdog', new Date().toISOString());
    logInfo('processApprovedInBatches', 'processed rows ' + start + '-' + end);
  } catch (e) {
    logError('processApprovedInBatches', e);   // checkpoint stays; safe resume
  }
}

/** Alert if a running job hasn't checkpointed within the timeout. */
function watchdog(timeoutMinutes) {
  timeoutMinutes = timeoutMinutes || 30;
  var last = PropertiesService.getScriptProperties().getProperty('kdp_watchdog');
  if (!last) return;
  var ageMin = (Date.now() - new Date(last).getTime()) / 60000;
  if (ageMin > timeoutMinutes) {
    sendCriticalAlert('KDP watchdog', 'No checkpoint for ' + Math.round(ageMin) + ' min');
  }
}

/** Clear checkpoint/watchdog so a stuck job restarts cleanly. */
function resetJob() {
  var props = PropertiesService.getScriptProperties();
  props.deleteProperty(CHECKPOINT_KEY);
  props.deleteProperty('kdp_watchdog');
  logInfo('resetJob', 'checkpoint cleared');
}

// ---- Test harness (pure helpers only) ------------------------------------

function runUnitTests() {
  var results = [];
  function check(name, cond) { results.push((cond ? 'PASS ' : 'FAIL ') + name); }

  var m = buildListMap([['list_name', 'value'], ['bleed', 'bleed'],
    ['bleed', 'no_bleed'], ['trim_size', '8.5x8.5']]);
  check('buildListMap groups values', m.bleed.length === 2 && m.trim_size[0] === '8.5x8.5');
  check('buildListMap skips header', m.list_name === undefined);

  check('colToLetter 1=A', colToLetter(1) === 'A');
  check('colToLetter 27=AA', colToLetter(27) === 'AA');

  check('headerIndex found', headerIndex(['task_id', 'title', 'bleed'], 'bleed') === 3);
  check('headerIndex missing', headerIndex(['a', 'b'], 'z') === -1);

  var now = new Date('2026-07-31T00:00:00Z');
  check('isExpired old', isExpired('2026-06-01T00:00:00Z', now, 30) === true);
  check('isExpired recent', isExpired('2026-07-30T00:00:00Z', now, 30) === false);
  check('isExpired bad-date', isExpired('not-a-date', now, 30) === false);

  var out = results.join('\n');
  Logger.log(out);
  var failed = results.filter(function (r) { return r.indexOf('FAIL') === 0; });
  if (typeof SpreadsheetApp !== 'undefined' && SpreadsheetApp.getUi) {
    SpreadsheetApp.getUi().alert('Self-tests\n\n' + out);
  }
  return { passed: results.length - failed.length, failed: failed.length, detail: out };
}
