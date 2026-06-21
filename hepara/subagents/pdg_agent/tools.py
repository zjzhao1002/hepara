import pdg

def get_all_particle_names():
    pdg_api = pdg.connect()
    all_data = pdg_api.get_all(data_type_key='PART')
    all_descriptions =[]
    for data in all_data:
        all_descriptions.append(data.description)
    return all_descriptions