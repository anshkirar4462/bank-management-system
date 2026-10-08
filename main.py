import json
import random
import string
from pathlib import Path

class Bank:
    database = 'data.json' # to access path of json file
    data = []
    try:
        if Path(database).exists():
            with open(database,'r') as fs:
                data = json.loads(fs.read()) 
        else:
            print("No such file exist")
    except Exception as err:
        print(f"An exception occured as {err}")

    @classmethod
    def __update(cls):
        with open(cls.database,'w')as fs:
            fs.write(json.dumps(cls.data))

    @classmethod
    def __accountgenerate(cls):
        alpha = random.choices(string.ascii_letters,k = 3)
        nums = random.choices(string.digits,k=3)
        spchar = random.choices("!@#$%&*", k=1)
        id = alpha + nums + spchar
        random.shuffle(id)
        return "".join(id)


    def Createaccount(self):
        info = {
            "name": input("Tell your name"),
            "age": int(input("Tell your age")),
            "email":(input("Tell your email")),
            "pin": int(input("Tell your pin")),
            "account no": Bank.__accountgenerate(),
            "Balance": 0
        }
        if info['age']<18 or len(str(info['pin']))!= 4 :
            print("Sorry you cannot create your account")
        else:
            print("Account has been created succesfully")
            for i in info:
                print(f"{i}:{info[i]}") 
            print("Please note down your Account number")
            Bank.data.append(info)
            Bank.__update()

    def depositmoney(self):
        acc_num = input("Please tell your acc_no : ")
        pin = int(input("Please tell your pin : "))

        userdata = [i for i in Bank.data if i['account no'] == acc_num and i['pin'] == pin]

        if userdata == False:
            print("Sorry no data found")
        else:
            amount = int(input("How much you want to deposit"))
            if amount > 10000 or amount < 0:
                print("Sorry you can deposit below 10000")
            else:
                
                userdata[0]['Balance'] += amount
                Bank.__update()
                print("Amount deposited successfully")


    def withdrawmoney(self):
        acc_num = input("Please tell your acc_no : ")
        pin = int(input("Please tell your pin : "))

        userdata = [i for i in Bank.data if i['account no'] == acc_num and i['pin'] == pin]

        if userdata == False:
            print("Sorry no data found")
        else:
            amount = int(input("How much you want to withdraw"))
            if userdata[0]['Balance'] < amount:
                print("Insufficient balance")
            else:
                
                userdata[0]['Balance'] -= amount
                Bank.__update()
                print("Amount withdrew successfully")


    def showdetails(self):
        acc_num = input("Please tell your acc_no : ")
        pin = int(input("Please tell your pin : "))
        userdata = [i for i in Bank.data if i['account no'] == acc_num and i['pin'] == pin]
        print("Your informations are \n\n\n")
        for i in userdata[0]:
            print(f"{i} : {userdata[0][i]}")       


    def updatedetails(self):
        acc_num = input("Please tell your acc_no : ")
        pin = int(input("Please tell your pin : "))
        userdata = [i for i in Bank.data if i['account no'] == acc_num and i['pin'] == pin]

        if userdata == False:
            print("No such user found")
        else:
            print("You cannot change the age, account number, balance")    

            print("Fill the details for change or leave it empty if no change" )

            newdata = {
                "name":input("Please tell new name or press Enter:"),
                "email":input("Please tell your new email or press enter to skip"),
                "pin": input("Please tell your new pin")

            }
            if newdata["name"] == "":
                newdata["name"] = userdata[0]['name']
            if newdata["email"] == "":
                newdata["email"] = userdata[0]['email']
            if newdata["pin"] == "":
                newdata["pin"] = userdata[0]['pin']

            newdata['age'] = userdata[0]['age']
            newdata['account no'] = userdata[0]['account no']
            newdata['Balance'] = userdata[0]['Balance'] 

            if type(newdata['pin']) == str:
                newdata['pin'] =  int(newdata['pin'])   

            for i in newdata:
                if newdata[i] == userdata[0][i]:
                    continue
                else:
                    userdata[0][i] = newdata[i]

            Bank.__update()
            print("Details updated successfully")


    def Delete(self):
        acc_num = input("Please tell your acc_no : ")
        pin = int(input("Please tell your pin : "))
        userdata = [i for i in Bank.data if i['account no'] == acc_num and i['pin'] == pin]

        if userdata == False:
            print("sorry no such data exist")
        else:
            check = input("press y if you actually want to delete the account or press n")
            if check == 'n' or check == "N":
                print("Bypassed")
            else:
                index = Bank.data.index(userdata[0])
                Bank.data.pop(index)
                print("Account deleted successfully")
                Bank.__update()


user = Bank()


print("Press 1 for creating an account")
print("Press 2 for depositing money in the bank")
print("Press 3 for withdrawing the money")
print("Press 4 for details fetching")
print("Press 5 for updating the details")
print("Press 6 for deleting your account")

check = int(input("Tell your response:- "))

if check == 1:
    user.Createaccount()

if check == 2:
    user.depositmoney()

if check == 3:
    user.withdrawmoney()

if check == 4:
    user.showdetails()

if check == 5:
    user.updatedetails()

if check == 6:
    user.Delete()
