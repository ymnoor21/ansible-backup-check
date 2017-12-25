#!/usr/bin/python
import json
import argparse
import sys
import os
import subprocess

daily_code_path = '/tmp/daily/codes'
daily_db_path = '/tmp/daily/databases'

weekly_code_path = '/tmp/weekly/codes'
weekly_db_path = '/tmp/weekly/databases'
weekly_files_path = '/tmp/weekly/files'

monthly_backup_path = '/tmp/monthly'
yearly_backup_path = '/tmp/yearly'

days = [
    'Saturday', 'Sunday',
    'Monday', 'Tuesday',
    'Wednesday', 'Thursday',
    'Friday'
]

codebases = ['application', 'website', 'personal', 'backend', 'api']

mysql_servers = ['db01', 'db02', 'db03']
redis_servers = ['redis01', 'redis02']


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

        for codebase in codebases:
            for day in days:
                code_file = "{}-code-backup-{}.tar.bz2".format(codebase, day)

                code_file_path = path + "/" + code_file

                if os.path.exists(code_file_path) and \
                        os.path.isfile(code_file_path):
                    code_backup_found += 1
                    code_backup_found_files.append({
                        "name": code_file_path,
                        "size": os.path.getsize(code_file_path)
                    })
                else:
                    code_backup_missing += 1
                    code_backup_missing_files.append(code_file_path)

        result = 1 if code_backup_missing >= 1 else 0
        message = "Missing files" if code_backup_missing >= 1 else ""

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

        for mysql_server in mysql_servers:
            for day in days:
                database_file = "mysql-backup-{}-{}.tar.bz2".\
                    format(mysql_server, day)

                database_file_path = path + "/" + database_file

                if os.path.exists(database_file_path) and \
                        os.path.isfile(database_file_path):
                    database_backup_found += 1
                    database_backup_found_files.append({
                        "name": database_file_path,
                        "size": os.path.getsize(database_file_path)
                    })
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
                    database_backup_found_files.append({
                        "name": database_file_path,
                        "size": os.path.getsize(database_file_path)
                    })
                else:
                    database_backup_missing += 1
                    database_backup_missing_files.append(database_file_path)

        result = 1 if database_backup_missing >= 1 else 0
        message = "Missing files" if database_backup_missing >= 1 else ""

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
            path + "/" + "api-data-backup-Saturday.tar.bz2",
            path + "/" + "backend-calendars-backup-Saturday.tar.bz2",
            path + "/" + "personal-uploads-backup-Saturday.tar.bz2",
            path + "/" + "website-uploads-backup-Saturday.tar.bz2"
        ]

        return self.check_random_backups(paths)

    def check_monthly_backup(self):
        paths = [
            monthly_backup_path + "/api-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/api-data-backup-Saturday.tar.bz",
            monthly_backup_path + "/application-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/backend-calendars-backup-Saturday.tar.bz2",
            monthly_backup_path + "/backend-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/mysql-backup-db01-Tuesday.tar.bz2",
            monthly_backup_path + "/mysql-backup-staging-Tuesday.tar.bz2",
            monthly_backup_path + "/mysql-backup-web02-Tuesday.tar.bz2",
            monthly_backup_path + "/redis-backup-web01-Sunday.tar.bz2",
            monthly_backup_path + "/redis-backup-web03-Sunday.tar.bz2",
            monthly_backup_path + "/personal-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/personal-uploads-backup-Saturday.tar.bz2",
            monthly_backup_path + "/website-code-backup-Tuesday.tar.bz2",
            monthly_backup_path + "/website-uploads-backup-Saturday.tar.bz2"
        ]

        data = {
            "all": self.check_random_backups(paths)
        }

        print(json.dumps(data))

    def check_yearly_backup(self):
        paths = [
            yearly_backup_path + "/api-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/api-data-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/application-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/backend-calendars-backup-Saturday.tar.bz2",
            yearly_backup_path + "/backend-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/mysql-backup-db01-Tuesday.tar.bz2",
            yearly_backup_path + "/mysql-backup-staging-Tuesday.tar.bz2",
            yearly_backup_path + "/mysql-backup-web02-Tuesday.tar.bz2",
            yearly_backup_path + "/redis-backup-web01-Tuesday.tar.bz2",
            yearly_backup_path + "/redis-backup-web03-Tuesday.tar.bz2",
            yearly_backup_path + "/personal-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/personal-uploads-backup-Saturday.tar.bz2",
            yearly_backup_path + "/website-code-backup-Tuesday.tar.bz2",
            yearly_backup_path + "/website-uploads-backup-Saturday.tar.bz2"
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

        for path in paths:
            if os.path.exists(path) and os.path.isfile(path):
                found += 1
                found_files.append({
                    "name": path,
                    "size": os.path.getsize(path)
                })
            else:
                missing += 1
                missing_files.append(path)

        result = 1 if missing >= 1 else 0
        message = "Missing files" if missing >= 1 else ""

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run automated scripts")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--backup',
                       help="Value = DAILY | WEEKLY | MONTHLY | YEARLY")

    args = vars(parser.parse_args())

    at = AutomatedTask()

    if args['backup']:
        at.check_backup(args['backup'])
