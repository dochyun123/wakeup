// 마감 기능 : 구글폼의 appscript
// 문자전송 기능 : 스프레드시트의 appscript

function UniqueID(e) {
  const sheet = e.range.getSheet();
  const submittedRow = e.range.getRow();

  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  let columnIndex = headers.indexOf("고유번호");

  // "고유번호" 열이 없으면 새로 생성
  if (columnIndex === -1) {
    Logger.log('There is no column 고유번호');
    sheet.insertColumnAfter(headers.length);
    sheet.getRange(1, headers.length + 1).setValue("고유번호");
    columnIndex = headers.length;
  }

  const cell = sheet.getRange(submittedRow, columnIndex + 1);
  if (!cell.getValue()) {
    cell.setValue(generateRandomString(30));
  }
}

function generateRandomString(length) {
  var prefix = "고유번호 앞자리 ex)WAKEUP";
  var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  var result = prefix;
  for (var i = 0; i < length - prefix.length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  Logger.log("고유번호: " + result);
  return result;
}



function QRcodeGenerate(e) {
  const sheet = e.range.getSheet();
  const lastRow = e.range.getRow();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var columnIndex = headers.indexOf("고유번호");
  var qrColumnIndex = headers.indexOf("QRcode");

  if (qrColumnIndex === -1) {
    Logger.log("QR링크가 있는 열이 없어서 추가합니다.")
    sheet.insertColumnAfter(headers.length);
    sheet.getRange(1, headers.length + 1).setValue("QRcode");
    qrColumnIndex = headers.length;
  }

  var existingQR = sheet.getRange(lastRow, qrColumnIndex + 1).getValue();
  if (existingQR) {
    Logger.log("이미 QR 코드가 존재합니다.");
    return;
  }
  
  var uniqueId = sheet.getRange(lastRow, columnIndex + 1).getValue();

  if (!uniqueId) {
    Logger.log("고유번호 없음");
    return;
  }

  var qrUrl = "https://quickchart.io/qr?text=" + encodeURIComponent(uniqueId) + "&size=400x400";
  Logger.log('QR링크:' + qrUrl);
  sheet.getRange(lastRow, qrColumnIndex + 1).setValue(qrUrl);
}



function sendMessage(e) {
  const sheet = e.range.getSheet();
  var row = e.range.getRow();
  var phoneNumber = sheet.getRange(row, 4).getValue();
  Logger.log("추출된 휴대폰 번호: " + phoneNumber);
  // 인증을 위해 헤더에 포함될 인증정보 생성
  var solapiKey = 'API key' // API KEY 입력
  var secret = 'secret key' // Seceret KEY 입력
  var now = new Date().toISOString()
  var genRanHex = size => [...Array(size)].map(() => Math.floor(Math.random() * 16).toString(16)).join('');
  var salt = genRanHex(64)
  var message = now + salt
  var byteSignature = Utilities.computeHmacSha256Signature(message, secret);
  var signature = byteSignature.reduce(function(str,chr){
    chr = (chr < 0 ? chr + 256 : chr).toString(16);
    return str + (chr.length === 1 ? '0' : '') + chr;
  },'');
  var url = "https://api.solapi.com/messages/v4/send-many/detail";
  var QRcode = sheet.getRange(row, 9).getValue();
  var data = { 
  messages: [{
    from : '보내는 번호',
    to: phoneNumber,
    text:`
메세지 내용

QR코드 링크:

${QRcode}
` 
}] 
}
  var response = UrlFetchApp.fetch(url, { 
    payload: JSON.stringify(data),
    method: 'post',
    headers: { Authorization: `HMAC-SHA256 apiKey=${solapiKey}, date=${now}, salt=${salt}, signature=${signature}`}, 
    contentType: 'application/json' 
  })
  var result = JSON.parse(response) || {};
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const logsheet = ss.getSheetByName('로그');
  var name = sheet.getRange(row, 2).getValue();
  var status = result.groupInfo.status;
  var failMessage = JSON.stringify(result.failedMessageList)
  // API 발송 결과에 대한 내용 출력
  logsheet.appendRow([
      phoneNumber,
      name,
      status,
      failMessage
    ]);

  }

function main(e) {
 // 제출된 응답 행 번호
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000); // 최대 30초 대기
    UniqueID(e);           // 고유번호 추가
    QRcodeGenerate(e);        // QR 생성
    sendMessage(e);           // 문자 전송
    /*sendAligo(e)*/
  
  } catch (error) {
    Logger.log("오류 발생: " + error);
  } finally {
    lock.releaseLock();
  }
}