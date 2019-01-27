import csv
import os

DEFAULT_ATTRS_HEADERS = [
    'added', 'zpid', 'url', 'price', 'zestimate', 'rent_zestimate','address', 'city', 'state', 'zipcode', 'beds', 'baths', 'sqft', 'home_type', 'home_status', 'facts', 'description', 'school_1_distance', 'latitude', 'longitude', 'school_1_grades', 'school_1_level', 'school_1_link', 'school_1_name', 'school_1_rating', 'school_1_size', 'school_1_students_per_teacher', 'school_2_distance', 'school_2_grades', 'school_2_level', 'school_2_link', 'school_2_name', 'school_2_rating', 'school_2_size', 'school_2_students_per_teacher', 'school_3_distance', 'school_3_grades', 'school_3_level', 'school_3_link', 'school_3_name', 'school_3_rating', 'school_3_size', 'school_3_students_per_teacher' ]

DEFAULT_PRICE_HEADERS = ["zpid","date", "price", "event", "agents"]

DEFAULT_TAX_HEADERS = ["zpid","property taxes", "year", "change", "tax assessment"]

def update_attrs_file(file_path, updates):
    return update_file(file_path, updates, headers=DEFAULT_ATTRS_HEADERS)

def update_tax_file(file_path, updates):
    return update_file(file_path, updates, headers=DEFAULT_TAX_HEADERS)

def update_price_file(file_path, updates):
    return update_file(file_path, updates, headers=DEFAULT_PRICE_HEADERS)

def update_file(file_path, updates, headers):
    if type(updates) is not list:
        updates = [updates]
    updates_filtered = [{k: v for k,v in d.items() if k in headers} for d in updates]
    write_header = not os.path.exists(file_path) # TODO: or empty file
    with open(file_path, 'a') as outfile:
        fp = csv.DictWriter(outfile, headers)
        if write_header:
            fp.writeheader()
        fp.writerows(updates_filtered)
    return file_path

def get_csv_col(csv_file, col_name):
    try:
        with open(csv_file, "r") as f:
            reader = csv.reader(f)
            cols = next(reader)
            if col_name in cols:
                zpid_idx = cols.index(col_name)
                read = [row[zpid_idx] for row in reader]
        return read
    except:
        return []

def delete_dups(in_file_name, out_file_name):
    seen = set()
    out_file = open(out_file_name, 'w')
    for line in open(in_file_name, 'r'):
        if line not in seen:
            out_file.write(line)
            seen.add(line)
    out_file.close()
