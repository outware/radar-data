import json
import gspread

################################################################################
#  Accessing Google Spreadsheets
################################################################################

SCOPE = ['https://spreadsheets.google.com/feeds']
CREDENTIALS_FN = 'credentials.json'

def open_sheet(spreadsheet, title):
    """Returns the first matching worksheet with title in spreadsheet."""
    data_sheets = filter(lambda sheet: sheet.title == title,
			 spreadsheet.worksheets())
    return data_sheets.pop()


def open_worksheet(spreadsheet_name,
		   worksheet_title):
    """Authenticate and open the a worksheet contained within a spreadsheet."""
    gc = login()
    spreadsheet = gc.open(spreadsheet_name)
    return open_sheet(spreadsheet, worksheet_title)


def file_path(relative_path):
    """Absolute directory from path relative 
    to the current working directory. 

    Arguments:
    relative_path -- relative path from the current working directory
    """

    import os
    relative_to_cwd = os.path.join(os.getcwd(),
				   os.path.dirname(__file__),
				   relative_path)
    return os.path.abspath(relative_to_cwd)

def login(scope=SCOPE, credentials_file_path=CREDENTIALS_FN):
    """OAUTH login to Google using JSON credentials file."""

    from oauth2client.client import SignedJwtAssertionCredentials
    credentials_path = file_path(credentials_file_path)
    with open(credentials_path, 'r') as credentials_file:
	json_key = json.load(credentials_file)
    	credentials = SignedJwtAssertionCredentials(
			json_key['client_email'],
			json_key['private_key'], scope)
       	gc = gspread.authorize(credentials)
	return gc
    return None


################################################################################

def default(func, exception, deflt):
    try:
	return func()
    except exception:
	return deflt



STATUS_OPTS = ['adopt', 'trial', 'assess', 'hold']


################################################################################
# Data transformation
################################################################################

def get_data_rows(wks):
    """Get rows excluding the header."""

    data_rows = wks.get_all_values()[1:]
    return data_rows


def status_from_flags(flags):
    """Translate list of flags into a radar status.
    Eg. ['', '', 'X', ''] -> 'assess' 
    """

    FLAG_INDEX = 1
    TITLE_INDEX = 0
    titled_flags = zip(STATUS_OPTS, flags)
    selected_titled_flag = filter(lambda x: len(x[FLAG_INDEX].strip()),
				  titled_flags)
    status = default(lambda: selected_titled_flag[0][TITLE_INDEX],
		     IndexError, None)
    return status


def get_quadrant(quadrants, quadrant_name):
    """Get quadrant item, if none exists in quadrants, then create."""

    # print "get_quadrant: quadrant_name = " + quadrant_name

    quadrant = None
    if not quadrants.has_key(quadrant_name):
	quadrant = {'name' : quadrant_name,
		    'adopt' : [], 'trial' : [], 'assess' : [], 'hold' : []}
	quadrants[quadrant_name] = quadrant
    else:
	quadrant = quadrants[quadrant_name]
    return quadrant


def build_quadrants(quadrants, rows, team):
    """Transform rows into quadrants and blips. Take quadrants param, add to it, and return."""

    for row in rows:
        quadrant_name, blip_name, desc_raw, public_raw, company_raw = row[:5]
        flag_values = row[5:9]
        quadrant = get_quadrant(quadrants, quadrant_name)
        status = status_from_flags(flag_values)
        desc = desc_raw.replace('\n', ' ')
        public = True if len(public_raw.strip()) else False
        company = True if len(company_raw.strip()) else False
        quadrant[status].append({'name' : blip_name,
				 'description': desc,
				 'public' : public,
				 'company' : company,
                 'team': team})
    return quadrants


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
	description='Transform Google Spreadheet radar data to Tech Radar compatible JSON.')
    parser.add_argument('--inputfile', dest='inputfile', required=True,
            help='filename, in json format, that contains a list of spreadsheet/worksheets as input')
    args = parser.parse_args()

    global log 
    log = False
    if log : print "Arguments: ", args
    
    if args.inputfile:
        with open(args.inputfile) as data_file:    
            data = json.load(data_file)

        quadrants = {}
        for spreadsheet_dic in data["radar-files"]:
            name = spreadsheet_dic["spreadsheet"]
            sheet = spreadsheet_dic["worksheet"]
            team = spreadsheet_dic["team"]

            if log : print "------------------------------------------------------------"
            if log : print name + ", " + sheet + ", " + team

            wks = open_worksheet(name, sheet)
            data_rows = wks.get_all_values()[1:]
            quadrants = build_quadrants(quadrants, data_rows, team)

        print json.dumps({'quadrants' : quadrants.values()})
        if log : print "*************************************************************"

        

    

