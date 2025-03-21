SHEET_NAME = "sico"
COUNTER_CELL = "E2"

function doGet(e) {
  var spreadSheet = SpreadsheetApp.getActiveSpreadsheet();
  var SHEET = spreadSheet.getSheetByName(SHEET_NAME);
  lastLog = SHEET.getRange(COUNTER_CELL).getValue();
  if (!lastLog) {
    lastLog = 0
  }
  lastLog = lastLog + 1;
  if (lastLog == 1) {
    lastLog = 2
  }
  SHEET.getRange(COUNTER_CELL).setValue(lastLog);
  ContentService.createTextOutput(SHEET.getRange("A"+lastLog).setValue(e.parameter.time));
  ContentService.createTextOutput(SHEET.getRange("B"+lastLog).setValue(e.parameter.temp));
  ContentService.createTextOutput(SHEET.getRange("C"+lastLog).setValue(e.parameter.pressure));

}