import psycopg2

def delete_db(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection):
    cur.execute("""
        DROP TABLE ClientsPhone;
    """)
    try:
        con.commit()
    except:
        return False
   
    cur.execute("""
        DROP TABLE Clients; 
    """)
    try:
        con.commit()
        if not  create_db(cur, con):
            print('Tables has delited, but i cant created the new tables!')
            return True
    except: return False
    return True

def create_db(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection)->bool:
    # delete_db(cur)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS  Clients(
            id SERIAL PRIMARY KEY,
            firstname VARCHAR(60) NOT NULL,
            secondname VARCHAR(60) NOT NULL,
            email VARCHAR(60) NOT NULL
            );
               
        CREATE TABLE IF NOT EXISTS ClientsPhone(
            id SERIAL primary key,
            client_id integer references Clients(id),
            phone varchar(15)
            );             
    """)
    try:
        con.commit()
        return True
    except:
        return False

def _find_client(cur:psycopg2.extensions.cursor, client_id:str = '', firstname:str = '', secondname:str = '', email:str = '', phone:str = '')->list:
    if client_id !='':
        cur.execute("""
            SELECT *
            FROM clients c
            WHERE c.id = %s;
        """, (client_id,))
    
    if firstname != '':
        cur.execute("""
            SELECT *
            FROM clients c
            WHERE c.firstname = %s;
        """, (firstname,))
    if secondname != '':
        cur.execute("""
            SELECT *
            FROM clients c 
            WHERE c.secondname = %s;
        """, (secondname,))
    if email != '':
        cur.execute("""
            SELECT *
            FROM clients c  
            WHERE c.email = %s;
        """, (email,))
    if phone != '':
        cur.execute("""
            SELECT c.id, firstname, secondname, email, cp.phone
            FROM clients c 
            LEFT JOIN clientsphone cp ON c.id = cp.client_id 
            WHERE cp.phone = %s;
        """, (phone,))
    try:
        data = cur.fetchall()
        data.insert(0,True)
        return data
    except:
        return [False] 

def _find_phones(cur:psycopg2.extensions.cursor, id:str):
    cur.execute("""
        select phone, id
        from clientsphone c 
        where client_id = %s;
    """, (str(id),))
    return cur.fetchall()

def find(cur:psycopg2.extensions.cursor):
    client_id = ''
    firstname = ''
    secondname = ''
    email = ''
    phone = ''
    while True:
        answ = input('\nFind by:\n1.ID\n2.first name\n3.second name\n4.email\n5.phone\n8.Continue\n9.Back\n')
        match answ:
            case '1': client_id = input('\nID: ')
            case '2': firstname = input('\nFirst name: ')
            case '3': secondname = input('\nSecond name: ')
            case '4': email = input('\nEmail: ')
            case '5': phone = input('\nPhone: ')
            case '8':
                result = _find_client(cur=cur,client_id=client_id, firstname=firstname, secondname=secondname, email=email, phone=phone)
                if result[0] == False:
                    print('Error! I cant make a request!')
                if len(result) <= 1:
                    print('\nThere is nothing!')
                print('\nResult:')
                for line in result[1:]:
                    phones = _find_phones(cur, line[0])
                    print(f'\n\tid: {line[0]},\n\tfirst name: {line[1]}, \n\tsecond name: {line[2]}, \n\temail: {line[3]}, \n\tphone: {'None' if len(phones)==0 else ' '+phones[0][0]}')
                    if len(phones)>1:
                        for x in phones[1:]:
                            print(f'\t\t{x[0]}')
                break
            case '9':
                break

def add_new_client(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection)->bool:
    firstname = input('\nFirst name: ')
    secondname = input('\nSecond name: ')
    email = input('\nEmail: ')
    cur.execute("""
        INSERT INTO clients(firstname, secondname, email) VALUES(%s, %s, %s);        
    """,(firstname, secondname, email))
    try:
        con.commit()
        return True
    except:
        return False

def add_phone(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection)->bool:
    client_id = input('\nEnter ID of client: ')
    result = _find_client(cur=cur, client_id=client_id)
    if result[0] == False:
        print('Error! I cant make a request!')
        return False
    if len(result) <= 1:
        print('\nThere is nothing!')
        return True
    found_client_id = result[1][0]
    phone = input('\nEnter phone number: ')
    cur.execute("""
        INSERT INTO clientsphone(client_id, phone) VALUES(%s, %s);
    """,(found_client_id, phone))
    try:
        con.commit()
        return True
    except:
        print('Error! I cant add phone!')
        return False

def _change_clients_details(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection, id:str, firstname:str, secondname:str, email:str)->bool:
    if firstname != '':
        cur.execute("""
        UPDATE clients
        SET firstname = %s
        WHERE id = %s;
    """, (firstname, id))
    if secondname != '':
        cur.execute("""
        UPDATE clients
        SET secondname = %s
        WHERE id = %s;
    """, (secondname, id))
    if email != '':
        cur.execute("""
        UPDATE clients
        SET email = %s
        WHERE id = %s;
    """, (email, id))
    try:
        con.commit()
        return True
    except:
        return False

def update_client(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection)->bool:
    client_id = input('\nEnter ID of client: ')
    result = _find_client(cur=cur, client_id=client_id)
    if result[0] == False:
        print('Error! I cant make a request!')
        return False
    if len(result) <= 1:
        print('\nThere is nothing!')
        return True
    firstname = ''
    secondname = ''
    email = ''    
    while True:
        answ = input('What you want to change?\n\t1.First name\n\t2.Second name\n\t3.Email\n\t8.Continue\n\t9.Back\n')
        match answ:
            case '1': firstname = input('\nNew firstname: ')
            case '2': secondname = input('\nNew secondname: ')
            case '3': email = input('\nNew email: ')
            case '8': 
               if _change_clients_details(cur, con, id=client_id, firstname=firstname, secondname=secondname, email=email):
                   return True
               else:
                   return False
            case '9':return True

def _delete_phones(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection, phone_id:str)->bool:
    cur.execute("DELETE FROM clientsphone WHERE id = %s", (phone_id,))
    try:
        con.commit()
        return True
    except:
        return False
def delete_phone(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection)->bool:
    client_id = input('\nEnter ID of client: ')
    result = _find_client(cur=cur, client_id=client_id)
    if result[0] == False:
        print('Error! I cant make a request!')
        return False
    if len(result) <= 1:
        print('\nThere is nothing!')
        return True
    phones = _find_phones(cur, client_id)
    if len(phones) == 0:
        print('\nThere is no phones!')
        return True
    else:
        print('\nWhich one?')
        for n, phone in enumerate(phones):
            print(f'{n+1}.{phone[0]}')
        y = int(input('\n'))
        if y-1 in range(n):
            answ = input('Are you sure?[y/n]: ')
            if answ == 'y':
                _delete_phones(cur, con, phones[y-1][1])
    return False

def delete_client(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection)->bool:
    client_id = input('\nEnter ID of client: ')
    result = _find_client(cur=cur, client_id=client_id)
    if result[0] == False:
        print('Error! I cant make a request!')
        return False
    if len(result) <= 1:
        print('\nThere is nothing!')
        return True
    answ = input('Are you sure to delete client?[y/n]: ')
    if answ == 'y':
        for phone in _find_phones(cur,client_id):
            _delete_phones(cur, con, phone[1])
        cur.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        try:
            con.commit()
            return True
        except:
            return False
    return True

def menu(cur:psycopg2.extensions.cursor, con:psycopg2.extensions.connection):
    print('Hello, Netology!\nThis is my DB homework!\n')
    while True:
        answ = input('There is functions you of my programs:\n1.Find\n2.Add new client\n3.Add phone to client\n4.Update clients detail\n5.Delete phone from client\n6.Delete client\n9.Quit\n')
        match answ:
            case '1':
                find(cur)
                print('\nDone!\n')
            case '2':
                if add_new_client(cur, con):
                    print('\nDone!\n')
                else: print('Error!')
            case '3':
                if add_phone(cur, con):
                    print('\nDone!\n')
                else: print('Error!')
            case '4': 
                if update_client(cur, con):
                    print('\nDone!\n')
                else: print('Error!')
            case '5':
                if delete_phone(cur, con):
                    print('\nDone!\n')
                else: print('Error!')
            case '6':
                if delete_client(cur, con):
                    print('\nDone!\n')
                else: print('Error!')
            case '9':
                break
            case 'delete db':
                answ = input('\nAre you sure that you want delete all tables?[y/n]\n')
                if answ == 'y':
                    delete_db(cur)
                    print('\nDone!\n')

def main():
    conn = psycopg2.connect(database = 'netologydb', user = 'postgres', password = '123321')
    with conn.cursor() as cur:
        menu(cur, conn)        
    conn.close() 

if __name__ == '__main__':
    main()