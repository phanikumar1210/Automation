from common import *

def get_file_data(file):
    try:
        data={}
        if not exists(file):
            file_object = open(file, "w")
            file_object.write('{}')
            file_object.close()
        with open(file, 'r+') as file_object:
            data = json.load(file_object)
            file_object.close()
        os.rename(file, file+"_old")
        return data
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))
        
def put_file_data(file,updated_data):
    try:
        with open(file, 'w') as file_object:
            json.dump(updated_data,file_object,indent=2, sort_keys=True)
            file_object.close()
        os.remove(file+"_old")
    except:
        logging.error("Exception occoured {} main".format(sys.exc_info()[1]))