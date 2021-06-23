master_json = {
    'issuer' : "*",
    "keywords" : ["*"],
    "fields" : [{
        "Default" : ["Default Value 115"]
    }],
    "tables" : [
        {
            "start" : "Default Value ",
            "end" : "Default Value",
            "body" : "Default Value"
        }
    ]
}
removed_json = {
    "Default" : "Default"
}
updated_json = {
    "Default" : "Default"
}
master_json_file = 'master_json.json'
master_template_folder = 'master_template'
master_template_yml_file = 'master.yml'
removed_json_file = 'removed_json.json'
updated_json_file = 'updated_json.json'
regex = r"(\S\ {0,3})+\ {0,5}\:{1}\ {0,5}(\S)+"
garbage_data = [
    'http',
    'https'
]
garbage_value = [
    '.com',
    '.in',
]
remove_initial_character =[
    ":",
    "-"
]