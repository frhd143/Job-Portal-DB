import mysql.connector
from mysql.connector import Error
import hashlib
import sys
from datetime import datetime

mydb = mysql.connector.connect (
    host = "localhost",
    user = "root",
    password = "farhad123!",
    auth_plugin = "mysql_native_password",
    database = "DBproject"
)

cursor = mydb.cursor()

def create_company ():
    company = "CREATE TABLE `Company` (" \
                "  `company_id` INT AUTO_INCREMENT PRIMARY KEY," \
                "  `company_name` varchar(255)," \
                "  `company_password` varchar(255)," \
                "  `description` varchar(255)" \
                ")"
    try:
        print("# Creating table 'Company'...")
        cursor.execute(company)
    except mysql.connector.Error as err:
        if err.errno == 1050:
            print("# Table already exists!")
        else:
            print("# Error: ", err)


def create_users ():
    users = "CREATE TABLE `Users` (" \
                    "  `P_number` VARCHAR(255) NOT NULL," \
                    "  `First_name` VARCHAR(255) NOT NULL," \
                    "  `Last_name` VARCHAR(255) NOT NULL," \
                    "  `user_password` varchar(255)," \
                    "  `tel_number` VARCHAR(255) NOT NULL," \
                    "  `email` VARCHAR(255) NOT NULL," \
                    "  `adress` VARCHAR(255) NOT NULL," \
                    "  PRIMARY KEY (`p_number`)" \
                    ")"
    try:
        print("# Creating table 'Users'...")
        cursor.execute(users)
    except mysql.connector.Error as err:
        if err.errno == 1050:
            print("# Table already exists!")
        else:
            print("# Error: ", err)


def create_jobs ():
    jobs = "CREATE TABLE `Jobs` (" \
                    "  `job_id` INT AUTO_INCREMENT PRIMARY KEY," \
                    "  `title` VARCHAR(255)," \
                    "  `description` VARCHAR(255)," \
                    "  `place` VARCHAR(255)," \
                    "  `date_created` Date," \
                    "  `company_id` INT," \
                    "  FOREIGN KEY (`company_id`) REFERENCES `Company`(`company_id`)" \
                    ")"
    try:
        print("# Creating table 'Jobs'...")
        cursor.execute(jobs)
    except mysql.connector.Error as err:
        if err.errno == 1050:
            print("# Table already exists!")
        else:
            print("# Error: ", err)


def create_applilcations():
    applications = "CREATE TABLE `Applications` (" \
                    "  `ref_id` INT AUTO_INCREMENT PRIMARY KEY," \
                    "  `P_number` VARCHAR(255)," \
                    "  `job_id` INT," \
                    "  FOREIGN KEY (`P_number`) REFERENCES `Users`(`P_Number`)," \
                    "  FOREIGN KEY (`job_id`) REFERENCES `Jobs`(`job_id`)" \
                    ")"
    try:
        print("# Creating table 'Applications'...")
        cursor.execute(applications)
    except mysql.connector.Error as err:
        if err.errno == 1050:
            print("# Table already exists!")
        else:
            print("# Error: ", err)


def add_company(company_name, passw, description):
    try:
        cursor.execute("SELECT `company_name` FROM Company WHERE `company_name` = %s", (company_name,))
        existing_company = cursor.fetchone()
        if existing_company:
            print("# Company already exists!")
        
        else:
            sql = "INSERT INTO `Company` (`company_name`, `company_password`,  `description`) VALUES (%s, %s, %s)"
            values = (company_name, passw, description)
            cursor.execute(sql, values)
            mydb.commit()
            print("# Company added successfully!")

    except mysql.connector.Error as err:
        mydb.rollback()
        print("# Error: ", err)
        

def add_users(p_number, first_name, last_name, passw,  tel_number, email, address):
    try:
        cursor.execute("SELECT `First_name` FROM Users WHERE `P_Number` = %s", (p_number,))
        existing_user = cursor.fetchone()
        if existing_user:
            print("# User already exists!")
        else:
            sql = "INSERT INTO `Users` (`P_number`, `First_name`, `Last_name`, `user_password`, `tel_number`, `email`, `adress`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (p_number, first_name, last_name, passw, tel_number, email, address)
            cursor.execute(sql, values)
            mydb.commit()
            print("# User added successfully.")
        
    except mysql.connector.Error as err:
        print("# Error:", err)
        mydb.rollback()
        

def add_jobs(title, description, place, date_created, company_name):
    try:
        # Check if Company exists
        cursor.execute("SELECT `company_id` FROM `Company` WHERE `company_name` = %s", (company_name,))
        company_id = cursor.fetchone()
        if company_id:
            # Check if job already exists in the table
            cursor.execute("SELECT `job_id` FROM `Jobs` WHERE `title` = %s AND `description` = %s AND `place` = %s AND `date_created` = %s AND `company_id` = %s", (title, description, place, date_created, company_id[0]))
            existing_job = cursor.fetchone()
            if existing_job:
                print("# Job already exists!")
            
            else:
                sql = "INSERT INTO `Jobs` (`title`, `description`, `place`, `date_created`, `company_id`) VALUES (%s, %s, %s, %s, %s)"
                values = (title, description, place, date_created, company_id[0])
                cursor.execute(sql, values)
                mydb.commit()
                print("# Job added successfully.")
        else:
            print("# Error: Company with provided name does not exist.")
    except mysql.connector.Error as err:
        print("# Error:", err)
        mydb.rollback()
        

def create_application_trigger():
    try:
        sql = '''
        CREATE TRIGGER application_prevent_duplicate 
        BEFORE INSERT ON Applications
        FOR EACH ROW
        
        BEGIN
            DECLARE existing_application INT;
            SELECT COUNT(*) INTO existing_application 
            FROM Applications 
            WHERE P_number = NEW.P_number AND job_id = NEW.job_id;
            IF existing_application > 0 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '# Application already exists!(inside the trigger)';
            END IF;
        END;
        '''
        cursor.execute(sql)
        #print("# Trigger 'application_prevent_duplicate' created successfully!")
    except mysql.connector.Error as err:
        print("# Error:", err)


def add_application(p_number, job_id):
    cursor.execute("DROP TRIGGER IF EXISTS application_prevent_duplicate")
    create_application_trigger()
    try:
        sql = "INSERT INTO Applications (P_number, job_id) VALUES (%s, %s)"
        values = (p_number, job_id)
        cursor.execute(sql, values)
        print("# Application submitted successfully")
        mydb.commit()
    except mysql.connector.Error as err:
        print("# Error:", err)
        mydb.rollback()


def get_available_jobs():
    jobs_sql = "SELECT * FROM jobs"
    cursor.execute(jobs_sql)
    jobs = cursor.fetchall()
    
    company_sql = "SELECT jobs.company_id, company_name FROM company INNER JOIN jobs ON company.company_id = jobs.company_id"
    cursor.execute(company_sql)
    company_detail = cursor.fetchall()
    if jobs:
        print("\n")
        for i in range(len(jobs)):
            ref_id = jobs[i][0]
            company = company_detail[i][1]
            title = jobs[i][1]
            description = jobs[i][2]
            place = jobs[i][3]
            published = jobs[i][4]
            print(f"- Job reference: {ref_id}")
            print(f"  Job Title: \t {title}")
            print(f"  Description: \t {description}")
            print(f"  Company: \t {company}")
            print(f"  Place: \t {place}")
            print(f"  Published: \t {published}")
            print("\n")
    else:
        print("# No open positions are available at the moment")


def user_login(user_p_num):
    cursor.execute("SELECT * FROM Users WHERE `P_Number` = %s", (user_p_num,))
    existing_user = cursor.fetchall()
    if existing_user:
        password_input = input("# Enter your password: \n>>> ")
        hashed_password_input = hashlib.md5(password_input.encode('utf-8')).hexdigest()

        cursor.execute("SELECT user_password FROM Users WHERE P_number = %s", (user_p_num,))
        retrieved_pass = cursor.fetchone()
        if retrieved_pass:
            retrieved_pass = retrieved_pass[0]
            if hashed_password_input == retrieved_pass:
                pass
            else:
                print("# Wrong password!")
                user_login(user_p_num)
    else:
        sign_up_input = input("\n# User does not exist! Do you want to sign up? (y for yes, n for no): \n>>> ")
        if sign_up_input == 'y':
            user_sign_up()
        else:
            return 0


def user_sign_up():
    personnum = input("\n# Enter your personnummer in this format (yymmddxxxx): \n>>> ")
    if len(personnum) == 10:
        cursor.execute("SELECT * FROM USERS WHERE p_number = %s", (personnum, ))
        existing_user = cursor.fetchall()
        if existing_user:
            print("# User already exists")
            return
        else:
            firstname = input("# Enter you firstname: \n>>> ")
            lastname = input("# Enter you lastname: \n>>> ")
            password =  input("# Enter your password: \n>>> ")
            password = password.encode('utf-8')
            hashed_pass = hashlib.md5(password)
            hashed_pass= hashed_pass.hexdigest()
            telefon = input("# Enter your telefon number: \n>>> ")
            email = input("# Enter your email address: \n>>> ")
            address = input("# Enter your address: \n>>> ")
            add_users(personnum, firstname, lastname, hashed_pass, telefon, email, address)
    else:
        print("# Wrong format!")
        user_sign_up()


def company_login(comp_name):
    cursor.execute("SELECT * FROM Company WHERE company_name = %s", (comp_name,))
    existing_company = cursor.fetchall()
    if existing_company:
        password_input = input("# Enter your password: \n>>> ")
        hashed_password_input = hashlib.md5(password_input.encode('utf-8')).hexdigest()
        
        cursor.execute("SELECT company_password FROM Company WHERE company_name = %s", (comp_name,))
        retrieved_pass = cursor.fetchone()
        if retrieved_pass:
            retrieved_pass = retrieved_pass[0]
            if hashed_password_input == retrieved_pass:
                pass
            else:
                print("# Wrong password!")
                company_login()
    else:
        sign_up_input = input("\n# Company does not exist! Do you want to sign up? (y for yes, n for no): \n>>> ")
        if sign_up_input == 'y':
            company_sign_up()
        else:
            return 0


def company_sign_up():
    company_name = input("\n# Please Enter your company name (ex. Region Blekinge): \n>>> ")
    cursor.execute("SELECT * FROM company WHERE company_name = %s", (company_name, ))
    existing_company = cursor.fetchall()
    if existing_company:
        print("# Company already exists")
        return
    else:
        description = input("# Describe your company in a few words: \n>>> ")
        password =  input("# Enter your password: \n>>> ")
        password = password.encode('utf-8')
        hashed_pass = hashlib.md5(password)
        hashed_pass= hashed_pass.hexdigest()
        add_company(company_name, hashed_pass, description)


def applicants(company_name):
    cursor.execute("SELECT company_id FROM Company WHERE company_name = %s", (company_name,))
    company_id = cursor.fetchone()
    if company_id:
        company_id = company_id[0]
        cursor.execute("SELECT * FROM Jobs WHERE company_id = %s", (company_id,))
        jobs = cursor.fetchall()
        for job in jobs:
            job_id = job[0]
            title = job[1]
            print("\nJob ID:", job_id)
            print("Title:", title)
            print("\nApplicants:")
            cursor.execute("SELECT P_number FROM Applications WHERE job_id = %s", (job_id,))
            applications = cursor.fetchall()
            if applications:
                for application in applications:
                    p_number = application[0]
                    cursor.execute("SELECT * FROM Users WHERE P_number = %s", (p_number,))
                    user = cursor.fetchone()
                    print("- P_number:", user[0])
                    print("  Name:", user[1], user[2])
                    print("  Email:", user[5])
            else:
                print("# No applicants for this job.")


def applied_jobs(pnummer):
    cursor.execute("SELECT * FROM Applications WHERE P_number = %s", (pnummer,))
    existing_applications = cursor.fetchall()
    if existing_applications:
        print("\n# Jobs you have applied to:")
        for application in existing_applications:
            job_id = application[2]
            cursor.execute("SELECT * FROM Jobs WHERE job_id = %s", (job_id,))
            job_details = cursor.fetchone()
            cursor.execute("SELECT company_name FROM Company WHERE company_id = %s", (job_details[5],))
            company_name = cursor.fetchone()
            print("- Job ID:", job_id)
            print("  Title:", job_details[1])
            print("  Description:", job_details[2])
            print("  Company:", company_name[0])
            print("\n")


def check_pnummer_fortmat(pnummber):
    if len(pnummber) == 10:
        return 1
    else:
        return 0


def create_remove_application_procedure():
    try:
        sql = '''
        CREATE PROCEDURE remove_application_procedure(
        IN pnummer_param VARCHAR(10),
        IN job_id_param INT
        )
        BEGIN
            DELETE FROM Applications WHERE P_number = pnummer_param AND job_id = job_id_param;
            SELECT ROW_COUNT() AS rows_deleted;
        END;
        '''
        cursor.execute(sql)
        #print("# Procedure 'remove_application_procecure' created successfully!")
    except mysql.connector.Error as err:
        print("# Error:", err)


def remove_application(pnummer, job_id):
    cursor.execute("DROP PROCEDURE IF EXISTS remove_application_procedure")
    create_remove_application_procedure()
    try:
        cursor.execute("select * from applications where p_number = %s and job_id = %s", (pnummer, job_id))
        existing_application = cursor.fetchall()
        if existing_application:
            cursor.callproc("remove_application_procedure", (pnummer, job_id))
            result = cursor.stored_results()
            for row in result:
                rows_deleted = row.fetchone()[0]
                print("# {} row(s) deleted s.".format(rows_deleted))
            mydb.commit()
        else:
            print("# The application does not exists")
    except mysql.connector.Error as err:
        print("Error:", err)
        mydb.rollback()


def remove_position(comp_name, job_id):
    cursor.execute("SELECT Company_id from Company WHERE company_name = %s", (comp_name, ))
    comp_id = cursor.fetchone()
    comp_id = comp_id[0]
    
    cursor.execute("SELECT * FROM Jobs where job_id = %s and company_id = %s", (job_id, comp_id ))
    existing_job = cursor.fetchall()
    if existing_job:
        cursor.execute("DELETE FROM Jobs WHERE job_id = %s and company_id = %s", (job_id, comp_id))
        print("# The job is removed successfully")
        mydb.commit()
    else:
        print("# This job does not exists")
        return


def comp_open_positions(comp_name):
    cursor.execute("SELECT Company_id from Company WHERE company_name = %s", (comp_name, ))
    comp_id = cursor.fetchone()
    comp_id = comp_id[0]
    cursor.execute("SELECT * FROM Jobs WHERE company_id = %s", (comp_id, ))
    jobs = cursor.fetchall()
    for job in jobs:
        jobs = job[0]
        print(f"- Job ID: {job[0]}")
        print(f"  Job Title: {job[1]}")
        print(f"  Description: {job[2]}")
        print(f"  Place: {job[3]}")
        print(f"  Published: {job[4]}")
        print("\n")


def drop_all_tables():
    sql_applications = "DROP TABLES IF EXISTS applications"
    sql_jobs = "DROP TABLES IF EXISTS Jobs"
    sql_company = "DROP TABLES IF EXISTS COMPANY"
    sql_user = "DROP TABLES IF EXISTS USERS"
    
    print("# Droping all tables...")
    cursor.execute(sql_applications)
    cursor.execute(sql_jobs)
    cursor.execute(sql_company)
    cursor.execute(sql_user)
    mydb.commit()


def create_all_tables():
    create_company()
    create_users()
    create_jobs()
    create_applilcations()

def main():    
    print("\n")
    print("Farhad Asadi")
    print("faas21@student.bth.se")
    print("------------------------")
    while True:
        print("\n# Choose an action? ")
        print("---------------------")
        print("\t1) Login as a Job Seeker\n \t2) Login as a Recruiter\n\t3) Open Positions \n\t4) Sign Up as a Job seeker \n\t5) Sign Up as a Recruiter \n\t9) Quit the program \n\n\t0) Restart the program (For developer only)")
        try:
            who_input = int(input(">>> "))
            ## User UI
            if who_input == 1:
                user_p_num = input("\n# Please Enter your personnummer in this format (yymmddxxxx): \n>>> ")
                format_check = check_pnummer_fortmat(user_p_num)
                if format_check == 1:
                    login_status = user_login(user_p_num)
                    if login_status == 0:
                        break
                    while True:
                        print("\n# Choose an action: \n--------------------- \n\t1) Open Positions \n\t2) Apply for a Position \n\t3) View your job applications")
                        print("\t4) Remove an application \n\t5) Log out \n\t9) Quit the program")
                        
                        action_input = int(input(">>> "))
                        if action_input == 1:
                            get_available_jobs()
                        elif action_input == 2:
                            job_id = int(input("# Enter the job reference you want to apply for: \n>>> "))
                            add_application(user_p_num, job_id)
                        elif action_input == 3:
                            applied_jobs(user_p_num)
                        elif action_input == 4:
                            ref_id = int(input("Enter the job_id of the application you want to remove: \n>>> "))
                            remove_application(user_p_num, ref_id)
                        elif action_input == 5:
                            break
                        elif action_input == 9:
                            return
                        else:
                            print("Invalid choice! Please try again.")
                            continue
                else:
                    print("# Invalid format. Try Again!")

            # Company UI
            elif who_input == 2:
                comp_name = input("\n# Please Enter your company's name (ex. Region Blekinge): \n>>> ")
                login_status = company_login(comp_name)
                if login_status == 0:
                    break
                while True:
                    print("\n# Choose the action: \n--------------------- \n\t1) Add a position \n\t2) Available applicants \n\t3) Remove a position \n\t4) View Open Positions \n\t5) Log out \n\t")
                    comp_act_input = int(input(">>> "))
                    if comp_act_input == 1:
                        title = input("# Enter the title of the position: \n>>> ")
                        description = input("# Describe the position with a few words: \n>>> ")
                        place = input("# Where is this position located?: \n>>> ")
                        today = datetime.today()
                        formatted_date = today.strftime("%Y-%m-%d")
                        add_jobs(title, description, place, formatted_date, comp_name)
                    elif comp_act_input == 2:
                        applicants(comp_name)
                    elif comp_act_input == 3:
                        job_id = int(input("Enter the job_id of the positioin you want to remove: \n>>> "))
                        remove_position(comp_name, job_id)
                    elif comp_act_input == 4:
                        comp_open_positions(comp_name)
                    elif comp_act_input == 5:
                        break
                    else:
                        print("Invalid choice! Please try again.")
                        continue
            elif who_input == 3:
                get_available_jobs()
            elif who_input == 4:
                user_sign_up()
            elif who_input == 5:
                company_sign_up()
            elif who_input == 9:
                return
            ## OBS! This can be used only to restart the program (i.e droping all tables and creating them)
            elif who_input == 0:
                drop_all_tables()
                create_all_tables()
            else:
                print("Invalid choice! Please try again.")
                continue
        except ValueError:
            print("# Invalid choice! Please try again. ")
            continue


main()