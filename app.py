import pymongo
import re


Mongo_URI = "mongodb://localhost:27017/"
client = pymongo.MongoClient(Mongo_URI)
db = client["CGS"]

customers = db["customers"]
orders = db["Orders"]
order_line_items = db["OrderLineItems"]

global_data = []
grouped_orders = []

     

def filter_edge_cases(line):
    #solve for spacing edge case (bad spacing)
    if "Representative 2817" in line:
        line = line.replace("Representative 2817","Representative  2817")
    if "Margarita Nueva" in line:
        line = line.replace("Margarita Nueva", "Margarita  Nueva")
    if "BerguvsvÃ¤gen  8" in line:
        line = line.replace("BerguvsvÃ¤gen  8","BerguvsvÃ¤gen 8")
    if "Mataderos  2312" in line:
        line = line.replace("Mataderos  2312", "Mataderos 2312")
    if "Wolski  Zajazd" in line:
        line = line.replace("Wolski  Zajazd", "Wolski Zajazd")
    if "Berkeley Gardens 12  Brewery" in line:
        line = line.replace("Berkeley Gardens 12  Brewery", "Berkeley Gardens 12 Brewery")

    #end solving for edge case
    return line

def eval_line(line):

    if line == "\n":
        return

    cleaned_lines = filter_edge_cases(line)

    #parse and put into array
    line_pre = re.sub('  +','<->',cleaned_lines).split('<->')
    
    

    #solves for edge cases (too little space)
    order_date = line_pre[12].split(" ")[0]
    required_date = line_pre[12].split(" ")[1]

    data_obj = {
        "customer_id" : line_pre[0],
        "company_name" : line_pre[1],
        "contact_name" : line_pre[2],
        "contact_title" : line_pre[3],
        "address" : line_pre[4],
        "city": line_pre[5],
        "region" : line_pre[6],
        "postal_code" : line_pre[7],
        "country" : line_pre[8],
        "phone" : line_pre[9],
        "fax": line_pre[10],
        "order_id": line_pre[11],
        "order_date": order_date,
        "required_date": required_date,
        "shipped_date": line_pre[13],
        "employee_id": line_pre[14],
        "freight": line_pre[15],
        "product_id": line_pre[16],
        "unit_price": line_pre[17],
        "quantity": line_pre[18],
        "discount": line_pre[19],
        
    }
          
    return data_obj

def read_file():
    file = open("CustomerOrders.txt","r")
    counter = 0
    inner_count = 0
    for line in file:
        counter += 1
        if counter > 2:
            fixedLine = eval_line(line)
            
            inner_count += 1
            global_data.append(fixedLine)


    

def Average(lst):
    return sum(lst) / len(lst)

def solve_for_Q1():
    
    for obj in global_data:
        if obj == None:
            break
        if not any(d["contact_name"] == obj["contact_name"] for d in grouped_orders):
            grouped_orders.append({"contact_name" : obj["contact_name"], "order_ids" : [ obj["order_id"] ] })
        else:
            for record in grouped_orders:
                if record["contact_name"] == obj["contact_name"]:
                    record["order_ids"].append(obj["order_id"])

   
    
    

    #orders grouped and ready to be accessed
    avg_list = []
    
    for member in grouped_orders:
        member["order_ids"] = list(set(member["order_ids"])) #removes duplicate orders
        avg_list.append(len(member["order_ids"]))
    
    
    print("average: " + str(round(Average(avg_list), 2)))



def solve_for_Q2():
    cust_arr = []
    file_cust_id = open("CustomerID.txt", "r")
    cust_counter = 0
    for line in file_cust_id:
        cust_counter += 1
        if cust_counter > 2:
            
            customer_id = line.replace('\n','')
            cust_arr.append(customer_id)
            #fills array with every customer in file
    file_cust_id.close()

    #check global variables for orders
    cust_copy = cust_arr
    for records in global_data:
        if records is None:
            break
        for i in range(0,len(cust_copy) - 1):
            if cust_copy[i] == records["customer_id"]:
                cust_copy.pop(i)
            
    print('no orders from: ')
    for customer_unordered in cust_copy:
        print(customer_unordered)



def solve_for_Q3():
    def inner_solve(currentAmount,unit_price, quantity, discount):
        total = (unit_price * quantity) - ((unit_price * quantity) * (discount / 100))
        return total + float(currentAmount)

    data = global_data
    obj_arr = []
    for rec in range(len(data)):
        if data[rec] is not None:
            if not any(d["order_id"] == data[rec]["order_id"] for d in obj_arr):
                dict_ref = {
                    "order_id" : data[rec]["order_id"],
                    "ongoing_amount" : inner_solve(0,float(data[rec]["unit_price"]), float(data[rec]["quantity"]), float(data[rec]["discount"]))
                }
                obj_arr.append(dict_ref)
            else:
                for obj in obj_arr:
                    if obj["order_id"] == data[rec]["order_id"]:
                        curr_amount = obj["ongoing_amount"]
                        obj["ongoing_amount"] = inner_solve(curr_amount,float(data[rec]["unit_price"]), float(data[rec]["quantity"]), float(data[rec]["discount"]))

    for roundMe in obj_arr:
        roundMe["ongoing_amount"] = round(roundMe["ongoing_amount"], 2)

    sorted_list_highest_pre = sorted(obj_arr, key = lambda i: i["ongoing_amount"], reverse=True)
    sorted_list_highest = sorted_list_highest_pre[0]
    sorted_list_lowest_pre = sorted(obj_arr, key = lambda i: i["ongoing_amount"], reverse=False)
    sorted_list_lowest = sorted_list_lowest_pre[0]


    print("highest obj: ")
    print(sorted_list_highest)
    print("lowest obj:")
    print(sorted_list_lowest)

def solve_for_Q4():
    data = global_data
    data_arr = []
    data_arr_global = []
    #solve for brazil
    for info in data:
        if info is not None:
            if info["country"] == "Brazil":
                if not any(d["product_id"] == info["product_id"] for d in data_arr):
                    full = float(info["quantity"])
                    data_arr.append({"product_id":info["product_id"], "full": full })
                else:
                    for el in data_arr:
                        if el["product_id"] == info["product_id"]:
                            curr = el["full"]
                            el["full"] = curr + (float(info["quantity"]))

    brazil_pre = sorted(data_arr, key = lambda i: i["full"], reverse=True)
    brazil = brazil_pre[0]

    print("brazil top object -> " + str(brazil))

    #solve for global
    for i2 in data:
        if i2 is not None:
            if not any(d["product_id"] == i2["product_id"] for d in data_arr_global):
                full = float(i2["quantity"])
                data_arr_global.append({"product_id":i2["product_id"], "full": full })
            else:
                for el in data_arr_global:
                    if el["product_id"] == i2["product_id"]:
                        curr = el["full"]
                        el["full"] = curr + (float(i2["quantity"]))

    global_pre = sorted(data_arr_global, key = lambda i: i["full"], reverse=True)
    globalEl = global_pre[0]
    print("global top object -> " + str(globalEl))




            


         

read_file()
print("-----------------")
print("\nquestion 1:\n")
solve_for_Q1()
print("-----------------")
print("\nquestion 2:\n")
solve_for_Q2()
print("-----------------")
print("\nquestion 3:\n")
solve_for_Q3()
print("-----------------")
print("\nquestion 4:\n")
solve_for_Q4()