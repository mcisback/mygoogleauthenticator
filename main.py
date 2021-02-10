from GoogleAuth import *
from CLI import *

import argparse

if __name__ == "__main__":
    config = ConfigManager()
    config.load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gui", help="Show GUI", action="store_true")
    parser.add_argument("-a", "--add", dest="add", help="Add Entry, example: Facebook:email", default='')
    parser.add_argument("-d", "--delete", dest="delete", help="Delete Entry, example: Facebook:email", default='')
    parser.add_argument("-get", "--get-entry", dest="get_entry", help="Show Entry And OTP, example: Facebook:email, returns OTP", default='')
    parser.add_argument("-nf", "--nice-formatting", dest="nice_formatting", help="Show Nice Formatting In Terminal",
                        action="store_true")
    parser.add_argument("-ss", "--show-secret", dest="show_secret", help="Show Secrets In Output, default: False",
                        action="store_true", default=False)
    parser.add_argument("-otp", "--show-otp", dest="show_otp", help="Show OTP if not shown",
                        action="store_true", default=False)
    parser.add_argument("-l", "--list-entries", dest="list_entries", help="List All Entries",
                        action="store_true")
    parser.add_argument("-s", "--secret", dest="secret", help="Add Entry Secret, example: FASDA212DAAD", default='')
    parser.add_argument("-sc", "--show-config", dest="show_config", help="Show Config Content And Path",
                        action="store_true")
    parser.add_argument("-cc", "--check-config", dest="check_config", help="Check Config Content",
                        action="store_true")

    options = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    if(options.gui):
        from GUI import MyGoogleAuthApp

        app = MyGoogleAuthApp()
        app.set_config(config)

        app.run()
    else:
        if options.show_config:
            print("CONFIG_PATH: ", config.CONFIG_FILE_PATH)
            print(config.get())

            sys.exit(0)
        elif options.check_config:
            try:
                is_config_ok = config.check_config(config.get())
            except (ValueError, TypeError) as err:
                print("Config Not Ok: ", err)
            except Exception as err:
                print("Config Not Ok: ", err)
            else:
                print("IS_CONFIG_OK ? ", str(is_config_ok))

            sys.exit(0)
        elif options.add:
            custom_id = options.add

            print("Adding: ", custom_id)

            if options.secret:
                secret = options.secret
            else:
                import getpass

                secret = ''

                while True:
                    secret = getpass.getpass('Secret: ')

                    if not secret:
                        print("Secret is empty, retry")
                    else:
                        break

            config.add_entry(custom_id, secret.upper())

            sys.exit(0)
        elif options.delete:
            if config.num_entries() <= 0:
                print("DB is Empty")
                sys.exit(0)

            custom_id = options.delete

            print("Deleting: ", custom_id)

            try:
                config.del_entry(custom_id)
            except KeyError:
                print(f"{custom_id} not found")

            sys.exit(0)
        elif options.list_entries:
            entries = config.list_entries()
            if len(entries) <= 0:
                print("DB is Empty")
                sys.exit(0)

            table_data = [
                ['#', 'KEY'],
            ]

            if options.show_secret:
                table_data[0].append('SECRET')

            if options.show_otp:
                table_data[0].append('OTP_CODE')
                table_data[0].append('TIME_REMAINING')

            i = 0
            for custom_id, secret_key in entries.items():
                a = [i, custom_id]

                if options.show_secret:
                    a.append(secret_key)

                if options.show_otp:
                    otp = generate_code_from_time(secret_key)

                    time_remaining = otp[1]
                    otp_code = otp[0]

                    a.append(otp_code)
                    a.append(time_remaining)

                table_data.append(a)

                i += 1

            if options.nice_formatting:
                from terminaltables import AsciiTable

                table = AsciiTable(table_data)
                print(table.table)
            else:
                for row in table_data:
                    for el in row:
                        print(f"{el}\t", end='')

                    print("\n", end='')

            sys.exit(0)
        elif options.get_entry:
            if config.num_entries() <= 0:
                print("DB is Empty")
                sys.exit(0)

            custom_id = options.get_entry

            try:
                secret_key = config.get_entry_by_key(custom_id)
            except KeyError:
                print(f"{custom_id} not found")
            else:
                otp = generate_code_from_time(secret_key)
                time_remaining = otp[1]
                otp_code = otp[0]

                if options.nice_formatting:
                    from terminaltables import AsciiTable

                    table_data = [
                        ['KEY', 'OTP_CODE', 'TIME_REMAINING'],
                        [custom_id, otp_code, time_remaining],
                    ]

                    if options.show_secret:
                        table_data[0].insert(1, 'SECRET')
                        table_data[1].insert(1, secret_key)

                    table = AsciiTable(table_data)
                    print(table.table)
                else:
                    header = "KEY\t"
                    row = f"{custom_id}\t"

                    if options.show_secret:
                        header += "SECRET\t"
                        row += f"{secret_key}\t"

                    header += "OTP_CODE\tTIME_REMAINING"
                    row += f"{otp_code}\t{time_remaining}"

                    print(header)
                    print(row)

            sys.exit(0)
        elif options.secret:
            print("Missing --add Option and Argument")
            sys.exit(0)


