import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from HttpRunnerManager.settings import EMAIL_SEND_USERNAME, EMAIL_SEND_PASSWORD


def send_email_reports(receiver, html_report_path):
    """
    定时任务邮件发送模块
    :param receiver: list: 收件人
    :param html_report_path: str：报告路径
    :return:
    """

    subject = "自动化执行报告"

    with io.open(html_report_path, 'r', encoding='utf-8') as stream:
        send_file = stream.read()

    att = MIMEApplication(send_file)
    att.add_header('Content-Disposition', 'attachment', filename='Reports.html')

    body = MIMEText("附件为接口自动化执行报告，请查收！")

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['from'] = EMAIL_SEND_USERNAME
    msg['to'] = receiver
    msg.attach(att)
    msg.attach(body)


    smtp = smtplib.SMTP()
    smtp.connect(host='mail.haiercash.com',port='25')
    smtp.login(EMAIL_SEND_USERNAME, EMAIL_SEND_PASSWORD)
    smtp.sendmail(EMAIL_SEND_USERNAME, receiver.split(','), msg.as_string())
    smtp.quit()


if __name__ == '__main__':
    send_email_reports('fangandong@haiercash.com', 'D:\pyProject\\report.html')
