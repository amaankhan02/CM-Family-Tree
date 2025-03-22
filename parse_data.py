import pandas as pd
import json

NAME_COL = 'Your Full Name'
BIRTH_DATE_COL = 'Your Date of Birth \n(MM/DD/YYYY)'
FATHER_NAME_COL = "Father's Full Name"
FATHER_BIRTH_DATE_COL = "Fathers Date of Birth\n(MM/DD/YYYY)"
MOTHER_NAME_COL = "Mother's Full Name"
MOTHER_BIRTH_DATE_COL = "Mothers Date of Birth\n(MM/DD/YYYY)"
SPOUSE_COL = "Your Spouse's Full Name"

class Person:
    def __init__(self, name, birth_data, person_id):
        self.name = name
        self.birth_data = birth_data
        self.id = person_id

        self.fid = None     # father id
        self.mid = None     # mother id
        self.pids = []      # partner ids


def add_all_people(df):
    # NOTE: for now, we are only using the name as the unique identifier. In future, change
    # this to (name, birth_date) pair
    
    people = {} # key = name, value = Person object. 
    id_to_person = {}   # key = id, value = Person object

    # Add all people to the people dictionary
    for index, row in df.iterrows():
        curr_name = row[NAME_COL].strip()
        father_name = row[FATHER_NAME_COL].strip()
        mother_name = row[MOTHER_NAME_COL].strip()
        
        
        if curr_name not in people:
            people[curr_name] = Person(curr_name, row[BIRTH_DATE_COL], len(people))
            id_to_person[people[curr_name].id] = people[curr_name]
        if father_name not in people:
            people[father_name] = Person(father_name, row[FATHER_BIRTH_DATE_COL], len(people))
            id_to_person[people[father_name].id] = people[father_name]
        if mother_name not in people:
            people[mother_name] = Person(mother_name, row[MOTHER_BIRTH_DATE_COL], len(people))
            id_to_person[people[mother_name].id] = people[mother_name]
        if not pd.isnull(row[SPOUSE_COL]) and row[SPOUSE_COL].strip() not in people:
            people[row[SPOUSE_COL].strip()] = Person(row[SPOUSE_COL].strip(), None, len(people))
            id_to_person[people[row[SPOUSE_COL].strip()].id] = people[row[SPOUSE_COL].strip()]
            
    return people, id_to_person
    
def update_parent_ids(df, people: dict[str, Person]):
    # Update the mid, fid of each person
    for index, row in df.iterrows():
        curr_name = row[NAME_COL].strip()
        father_name = row[FATHER_NAME_COL].strip()
        mother_name = row[MOTHER_NAME_COL].strip()
        
        people[curr_name].fid = people[father_name].id
        people[curr_name].mid = people[mother_name].id
    
def update_partner_ids(df, people: dict[str, Person], id_to_person: dict[int, Person]):
    # Add the pids of each person based on the Spouse column
    for index, row in df.iterrows():
        curr_name = row[NAME_COL].strip()
        if pd.isnull(row[SPOUSE_COL]):
            continue
        spouse_name = row[SPOUSE_COL].strip()
        if spouse_name:
            people[curr_name].pids.append(people[spouse_name].id)
        
    # Go through all people, and pair the mid and fid to be each others pids since they're partners
    for person in people.values():
        if person.mid is None or person.fid is None:
            continue
        
        mother = id_to_person[person.mid]
        father = id_to_person[person.fid]
        
        if mother.id not in father.pids:
            father.pids.append(mother.id)
        if father.id not in mother.pids:
            mother.pids.append(father.id)

def save_to_json(people: dict[str, Person], save_filename):
    """
    Writes the people dictionary into a json file saving the Person object information
    """
    output = {}
    for name, person in people.items():
        output[name] = {
            'id': person.id,
            'name': person.name,
            'birth_date': str(person.birth_data),
            'fid': person.fid,
            'mid': person.mid,
            'pids': person.pids
        }
    
    with open(save_filename, 'w') as f:
        json.dump(output, f, indent=4)


def main():
    df = pd.read_excel('test_data_shortened.xlsx')
    people, id_to_person = add_all_people(df)
    update_parent_ids(df, people)
    update_partner_ids(df, people, id_to_person)
    
    save_to_json(people, 'test_family_tree.json')
    
if __name__ == "__main__":
    main()