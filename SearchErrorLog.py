# -*-coding:utf-8-*-
# author by 何瑞
import logging
import os
import shutil
import socket
import time
import subprocess
from typing import Dict, Any

import mysql.connector
from configparser import ConfigParser


def get_host_ip() -> object:
    """

    :rtype: str:返回本机IP
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
        return ip


def get_logfile_path(jy_tag: str) -> object:
    """
    :rtype: str:返回交易日志檔案的絕對路徑
    """
    if not os.path.exists('config.ini'):
        print('config.ini file is not exists, Please check it ...')
        exit()

    conf = ConfigParser()
    conf.read('config.ini')
    logfile_dir = conf.get('JyLog', jy_tag)

    # 拼接當前作業系統時間交易日志檔案的絕對路徑 (logfile_path), 比如 2021091709.log
    logfile_path: object = os.path.join(logfile_dir, time.strftime("%Y%m%d%H" + '.log', time.localtime()))
    return logfile_path


def get_errormessage_path(logfile_path: object) -> object:
    """
    :rtype: str:返回交易日志檔案的錯誤訊息
    """
    if not os.path.exists(logfile_path):
        print(
            '{} file is not exists, Please check it ... (Tips: Maybe the operating system time is not correct)'.format(
                logfile_path))
        exit()

    CMD = r'findstr "ErrorMessage=["' + " " + logfile_path
    try:
        error_message = subprocess.check_output(CMD).decode('GBK').replace('\r\n', '\n')
    except subprocess.CalledProcessError as e:
        print(e.output)

    jyerrorlog_dir = r'C:/JyErrorLog/'

    if not os.path.exists(jyerrorlog_dir):
        os.mkdir(jyerrorlog_dir)
    else:
        shutil.rmtree(jyerrorlog_dir)
        os.mkdir(jyerrorlog_dir)

    errormessage_path: object = os.path.join(jyerrorlog_dir, time.strftime("%Y%m%d%H" + '.error', time.localtime()))
    with open(errormessage_path, 'a+', encoding='utf-8') as f:
        f.write(error_message)

    time.sleep(3)

    if os.path.getsize(errormessage_path):
        return errormessage_path
    else:
        print('{} 为空，程式即將退出 ...'.format(errormessage_path))
        exit()


def insert_data_mysql(add_sql, data_sql) -> object:

    conf = ConfigParser()
    conf.read('config.ini')
    db_ip = conf.get('MySQL', 'IP')
    port = conf.get('MySQL', 'Port')
    username = conf.get('MySQL', 'username')
    password = conf.get('MySQL', 'password')
    dbname = conf.get('MySQL', 'dbname')

    try:
        cnx = mysql.connector.connect(user=username, password=password, host=db_ip, port=port,
                                      database=dbname)
        cursor = cnx.cursor()
    except mysql.connector.Error as err:
        logging.error('資料庫連接失敗: {}'.format(err))
        exit()

    try:
        cursor.execute(create_table_sql)
        cursor.execute(add_sql, data_sql)
        cnx.commit()
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        cnx.rollback()


host_ip = get_host_ip()
ptjy_tag = r'ptjy'
ptjy_logfile_path = get_logfile_path(ptjy_tag)

ptjy_errormessage_path = get_errormessage_path(ptjy_logfile_path)

table_name = time.strftime("%Y%m%d", time.localtime())

create_table_sql: str = (f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
                         f"                ID INT NOT NULL AUTO_INCREMENT, \n"
                         f"                IP CHAR(15),\n"
                         f"                FileName CHAR(50),\n"
                         f"                JyTag CHAR(5),\n"
                         f"                ErrorMessage CHAR(200),\n"
                         f"                PRIMARY KEY(ID))\n"
                         f"                ")

add_error_message: str = (f"INSERT INTO `{table_name}` "
                          "(ID, IP, FileName, JyTag, ErrorMessage) "
                          "VALUES (%(ID)s, %(IP)s, %(FileName)s, %(JyTag)s, %(ErrorMessage)s)")


with open(ptjy_errormessage_path, 'r', encoding='utf-8') as f:
    for err_line in f:
        data_error_message: Dict[str, Any] = \
            {'ID': None, 'IP': host_ip, 'FileName': ptjy_logfile_path, 'ErrorMessage': err_line, 'JyTag': ptjy_tag}
        insert_data_mysql(add_error_message, data_error_message)
