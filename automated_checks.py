#!/usr/bin/python
from __future__ import division
import json
import argparse
import sys
import os
import subprocess
import datetime

daily_code_path = '/tmp/backup/daily/codes'
daily_db_path = '/tmp/backup/daily/db'

weekly_code_path = '/tmp/backup/weekly/codes'
weekly_db_path = '/tmp/backup/weekly/db'
weekly_files_path = '/tmp/backup/weekly/files'

current_month_name = datetime.datetime.now().strftime("%B")
current_month = int(datetime.datetime.now().strftime("%m"))
current_year = int(datetime.datetime.now().strftime("%Y"))

monthly_backup_path = '/tmp/backup/monthly/' + current_month_name
yearly_backup_path = '/tmp/backup/' + str(current_year)

days = [
    'Saturday', 'Sunday',
    'Monday', 'Tuesday',
    'Wednesday', 'Thursday',
    'Friday'
]

codebases = ['cdn1', 'cdn2', 'cdn3', 'cdn4', 'cdn5']

mysql_servers = ['db1', 'db2', 'db3']
redis_servers = ['red1', 'red3']

codebase_sizes = {
    'cdn1': '169869312', # 162M
    'cdn2': '11534336', # 11M
    'cdn3': '60817408', # 58M
    'cdn4': '39845888', # 38M
    'cdn5': '25165824' # 24M
}

mysql_db_sizes = {
    'db1': '324009984', # 309M
    'db2': '27262976', # 26M
    'db3': '38797312' # 37M
}

redis_db_sizes = {
    'red1': '204800-716800', # 200K-700K
    'red3': '81920-122880' # 80K-120K
}

general_file_sizes = {
    weekly_files_path + '/cdn5-data-backup-Saturday.tar.bz2': '1503238553.6', # 1.4G
    weekly_files_path + '/cdn1-sam-backup-Saturday.tar.bz2': '12582912', # 12M
    weekly_files_path + '/cdn3-images-backup-Saturday.tar.bz2': '1503238553.6', # 1.4G
    weekly_files_path + '/cdn4-images-backup-Saturday.tar.bz2': '909115392', # 867M
    monthly_backup_path + '/cdn5-code-backup-Tuesday.tar.bz2': '25060966.4', # 23.9M
    monthly_backup_path + '/cdn5-data-backup-Saturday.tar.bz': '1503238553.6', # 1.4G
    monthly_backup_path + '/cdn2-code-backup-Tuesday.tar.bz2': '11219763.2', # 10.7M
    monthly_backup_path + '/cdn1-sam-backup-Saturday.tar.bz2': '12163481.6', # 11.6M
    monthly_backup_path + '/cdn1-code-backup-Tuesday.tar.bz2': '172700467.2', # 164.7M
    monthly_backup_path + '/mysql-backup-db1-Tuesday.tar.bz2': '330720870.4', # 315.4M
    monthly_backup_path + '/mysql-backup-db2-Tuesday.tar.bz2': '27472691.2', # 26.2M
    monthly_backup_path + '/mysql-backup-db3-Tuesday.tar.bz2': '37224448', # 35.5M
    monthly_backup_path + '/redis-backup-red1-Sunday.tar.bz2': '392499.2', # 383.3k
    monthly_backup_path + '/redis-backup-red3-Sunday.tar.bz2': '90828.8', # 88.7k
    monthly_backup_path + '/cdn3-code-backup-Tuesday.tar.bz2': '60188262.4', # 57.4M
    monthly_backup_path + '/cdn3-images-backup-Saturday.tar.bz2': '1503238553.6', # 1.4G
    monthly_backup_path + '/cdn4-code-backup-Tuesday.tar.bz2': '39321600', # 37.5M
    monthly_backup_path + '/cdn4-images-backup-Saturday.tar.bz2': '931240345.6', # 888.1M
}

# Setup acceptable file size percentage value
acceptable_size_percent = 0.25


class AutomatedTask:

    def check_backup(self, frequency):
        func = "check_%s_backup" % str.lower(frequency)
        if hasattr(AutomatedTask, func):
            getattr(self, func)()
        else:
            print(
                json.dumps({
                    "result": 1,
                    "message": "Invalid backup frequency"
                })
            )

    def check_daily_backup(self):
        output = {
            "codes": self.check_daily_or_weekly_code_backup(daily_code_path),
            "databases": self.check_daily_or_weekly_database_backup(
                daily_db_path
            )
        }

        print(json.dumps(output))

    def check_daily_or_weekly_code_backup(self, path):
        code_backup_found = 0
        code_backup_missing = 0

        code_backup_found_files = []
        code_backup_missing_files = []

        msg = ""
        msg_cnt = 0

        for codebase in codebases:
            for day in days:
                code_file = "{}-code-backup-{}.tar.bz2".format(codebase, day)

                code_file_path = path + "/" + code_file

                if os.path.exists(code_file_path) and \
                        os.path.isfile(code_file_path):
                    code_backup_found += 1

                    file_size = os.path.getsize(code_file_path)

                    size = humanize_bytes(file_size)[0]
                    suffix = humanize_bytes(file_size)[1]

                    msg = check_file_size(file_size, codebase_sizes, codebase)

                    if msg:
                        msg_cnt += 1
                        info = {
                            "name": code_file_path,
                            "size": size + suffix,
                            "error": msg
                        }
                    else:
                        info = {
                            "name": code_file_path,
                            "size": size + suffix,
                        }

                    code_backup_found_files.append(info)
                else:
                    code_backup_missing += 1
                    code_backup_missing_files.append(code_file_path)

        result = 1 if code_backup_missing >= 1 else 1 if msg_cnt >= 1 else 0
        message = "Missing files" if len(
            code_backup_missing_files) >= 1 else msg if msg else ""

        return {
            "result": result,
            "message": message,
            "found": {
                "count": code_backup_found,
                "files": code_backup_found_files
            },
            "missing": {
                "count": code_backup_missing,
                "files": code_backup_missing_files
            }
        }

    def check_daily_or_weekly_database_backup(self, path):
        database_backup_found = 0
        database_backup_missing = 0

        database_backup_found_files = []
        database_backup_missing_files = []

        msg1 = ""
        msg2 = ""
        msg1_cnt = 0
        msg2_cnt = 0

        for mysql_server in mysql_servers:
            for day in days:
                database_file = "mysql-backup-{}-{}.tar.bz2".\
                    format(mysql_server, day)

                database_file_path = path + "/" + database_file

                if os.path.exists(database_file_path) and \
                        os.path.isfile(database_file_path):
                    database_backup_found += 1

                    file_size = os.path.getsize(database_file_path)

                    size = humanize_bytes(file_size)[0]
                    suffix = humanize_bytes(file_size)[1]

                    msg1 = check_file_size(
                        file_size, mysql_db_sizes, mysql_server)

                    if msg1:
                        msg1_cnt += 1
                        info = {
                            "name": database_file_path,
                            "size": size + suffix,
                            "error": msg1
                        }
                    else:
                        info = {
                            "name": database_file_path,
                            "size": size + suffix,
                        }

                    database_backup_found_files.append(info)
                else:
                    database_backup_missing += 1
                    database_backup_missing_files.append(database_file_path)

        for redis_server in redis_servers:
            for day in days:
                database_file = "redis-backup-{}-{}.tar.bz2".\
                    format(redis_server, day)

                database_file_path = path + "/" + database_file

                if os.path.exists(database_file_path) and \
                        os.path.isfile(database_file_path):
                    database_backup_found += 1

                    file_size = os.path.getsize(database_file_path)

                    size = humanize_bytes(file_size)[0]
                    suffix = humanize_bytes(file_size)[1]

                    msg2 = check_file_size(
                        file_size, redis_db_sizes, redis_server)

                    if msg2:
                        msg2_cnt += 1
                        info = {
                            "name": database_file_path,
                            "size": size + suffix,
                            "error": msg2
                        }
                    else:
                        info = {
                            "name": database_file_path,
                            "size": size + suffix,
                        }

                    database_backup_found_files.append(info)
                else:
                    database_backup_missing += 1
                    database_backup_missing_files.append(database_file_path)

        result = 1 if database_backup_missing >= 1 else 1 if msg1_cnt >= 1 or msg2_cnt >= 1 else 0
        message = "Missing files" if len(
            database_backup_missing_files) >= 1 else msg1 if msg1 else msg2 if msg2 else ""

        return {
            "result": result,
            "message": message,
            "found": {
                "count": database_backup_found,
                "files": database_backup_found_files
            },
            "missing": {
                "count": database_backup_missing,
                "files": database_backup_missing_files
            }
        }

    def check_weekly_backup(self):
        output = {
            "codes": self.check_daily_or_weekly_code_backup(weekly_code_path),
            "databases": self.check_daily_or_weekly_database_backup(
                weekly_db_path
            ),
            "files": self.check_weekly_files_backup(weekly_files_path)
        }

        print(json.dumps(output))

    def check_weekly_files_backup(self, path):
        paths = [
            path + "/" + "cdn5-data-backup-Saturday.tar.bz2",
            path + "/" + "cdn1-sam-backup-Saturday.tar.bz2",
            path + "/" + "cdn3-images-backup-Saturday.tar.bz2",
            path + "/" + "cdn4-images-backup-Saturday.tar.bz2"
        ]

        return self.check_random_backups(paths)

    def check_monthly_backup(self):
        paths = [
            monthly_backup_path + "/cdn5-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/cdn5-data-backup-Saturday.tar.bz",
            monthly_backup_path + "/cdn2-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/cdn1-sam-backup-Saturday.tar.bz2",
            monthly_backup_path + "/cdn1-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/mysql-backup-db1-Tuesday.tar.bz2",
            monthly_backup_path + "/mysql-backup-db2-Tuesday.tar.bz2",
            monthly_backup_path + "/mysql-backup-db3-Tuesday.tar.bz2",
            monthly_backup_path + "/redis-backup-red1-Sunday.tar.bz2",
            monthly_backup_path + "/redis-backup-red3-Sunday.tar.bz2",
            monthly_backup_path + "/cdn3-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/cdn3-images-backup-Saturday.tar.bz2",
            monthly_backup_path + "/cdn4-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/cdn4-images-backup-Saturday.tar.bz2"
        ]

        data = {
            "all": self.check_random_backups(paths)
        }

        print(json.dumps(data))

    def check_yearly_backup(self):
        paths = [
            yearly_backup_path + "/cdn5-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/cdn5-data-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/cdn2-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/cdn1-sam-backup-Saturday.tar.bz2",
            yearly_backup_path + "/cdn1-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/mysql-backup-db1-Tuesday.tar.bz2",
            yearly_backup_path + "/mysql-backup-db2-Tuesday.tar.bz2",
            yearly_backup_path + "/mysql-backup-db3-Tuesday.tar.bz2",
            yearly_backup_path + "/redis-backup-red1-Tuesday.tar.bz2",
            yearly_backup_path + "/redis-backup-red3-Tuesday.tar.bz2",
            yearly_backup_path + "/cdn3-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/cdn3-images-backup-Saturday.tar.bz2",
            yearly_backup_path + "/cdn4-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/cdn4-images-backup-Saturday.tar.bz2"
        ]

        data = {
            "all": self.check_random_backups(paths)
        }

        print(json.dumps(data))

    def check_random_backups(self, paths):
        found = 0
        missing = 0
        missing_files = []
        found_files = []
        msg = ""
        msg_cnt = 0

        for path in paths:
            if os.path.exists(path) and os.path.isfile(path):
                found += 1

                file_size = os.path.getsize(path)

                size = humanize_bytes(file_size)[0]
                suffix = humanize_bytes(file_size)[1]

                msg = check_file_size(file_size, general_file_sizes, path)

                if msg:
                    msg_cnt += 1

                    info = {
                        "name": path,
                        "size": size + suffix,
                        "error": msg
                    }
                else:
                    info = {
                        "name": path,
                        "size": size + suffix,
                    }

                found_files.append(info)
            else:
                missing += 1
                missing_files.append(path)

        result = 1 if missing >= 1 else 1 if msg_cnt >= 1 else 0

        message = "Missing files" if len(
            missing_files) >= 1 else msg if msg else ""

        return {
            "result": result,
            "message": message,
            "found": {
                "count": found,
                "files": found_files
            },
            "missing": {
                "count": missing,
                "files": missing_files
            }
        }


def humanize_bytes(bytes, precision=2):
    abbrevs = (
        (1 << 50L, 'P'),
        (1 << 40L, 'T'),
        (1 << 30L, 'G'),
        (1 << 20L, 'M'),
        (1 << 10L, 'K'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1B'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return ['%.*f' % (precision, bytes / factor), suffix]


def check_file_size(file_size, dict_to_search, key_to_search):
    msg = ""

    try:
        if dict_to_search[key_to_search]:
            splt = dict_to_search[key_to_search].split('-')

            try:
                size_range = [float(splt[0]), float(splt[1])]
            except IndexError:
                low_limit = float(splt[0]) - float(splt[0]) * \
                    acceptable_size_percent
                high_limit = float(splt[0]) + float(splt[0]) * \
                    acceptable_size_percent
                size_range = [low_limit, high_limit]

            if file_size >= size_range[0] and file_size <= size_range[1]:
                msg = ""
            else:
                if len(splt) >= 2:
                    hbl = humanize_bytes(size_range[0])
                    hbl_size = hbl[0]
                    hbl_suffix = hbl[1]

                    hbh = humanize_bytes(size_range[1])
                    hbh_size = hbh[0]
                    hbh_suffix = hbh[1]

                    if file_size < size_range[0]:
                        msg = "File size is smaller than acceptable size. "
                    elif file_size > size_range[1]:
                        msg = "File size is larger than acceptable size. "

                    msg = msg + "The size should be within {}{}-{}{} range.".format(
                        hbl_size, hbl_suffix, hbh_size, hbh_suffix)
                else:
                    hb = humanize_bytes(
                        float(dict_to_search[key_to_search]))
                    hb_size = hb[0]
                    hb_suffix = hb[1]

                    if file_size < size_range[0]:
                        msg = "File size is smaller than acceptable size. "
                    elif file_size > size_range[1]:
                        msg = "File size is larger than acceptable size. "

                    msg = msg + "Original file size was {}{}".format(
                        hb_size, hb_suffix)
        else:
            msg = "Size value missing"
    except KeyError:
        msg = "File size missing"

    return msg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run automated scripts")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--backup',
                       help="Value = DAILY | WEEKLY | MONTHLY | YEARLY")

    args = vars(parser.parse_args())

    at = AutomatedTask()

    if args['backup']:
        at.check_backup(args['backup'])

