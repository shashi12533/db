import json
from flask import Blueprint, request, abort, jsonify, current_app, Response

from db import db
from db.api.errors import CustomError400
import db.api.utils as utils
import db.helper.label as label
import db.api.queries as queries

from db.api.queries import Allowed
from db.api.parameters import RequestArgs, RequestFrameArgs


api = Blueprint('api', __name__, url_prefix='/api')


# FIXME: this shuts down validation error messages

# Return validation errors as JSON
@api.errorhandler(400)
def handle_validation_error(err):
    exc = err.exc
    return jsonify({'errors': exc.messages}), 422

#@api.errorhandler(CustomError400)
#def handle_invalid_usage(error):
#    """
#    Generate a json object of a custom error
#    """
#    response = jsonify(error.to_dict())
#    response.status_code = error.status_code
#    return response


@api.route('/datapoints', methods=['POST'])
def upload_data():
    """
    Upload incoming data to database.
    ---
    tags:
        - datapoints
    parameters:
       - name: API_TOKEN
         in: query
         type: string
         required: true
         description: API key
       - name: data
         in: query
         type: list
         required: true
         description: List of dictionaries to upload
    responses:
        403:
            description: Failed to authenticate correctly.
        200:
            description: Returns empty dictionary on success.
    """
    # authorisation
    token_to_check = RequestArgs()['API_TOKEN']
    if token_to_check != current_app.config['API_TOKEN']:
        return abort(403)
    # upload data
    try:
        data = json.loads(request.data)
        for datapoint in data:
            queries.upsert(datapoint)
        db.session.commit()
        return jsonify({})
    except:
        db.session.rollback()
        return abort(400)


@api.route('/datapoints', methods=['GET'])
def get_datapoints():
    """
    Returns formatted data of specified name and frequency
    ---
    tags:
        - datapoints
    parameters:
      - name: name
        in: query
        type: string
        required: true
        description: the datapoint name
      - name: freq
        in: query
        type: string
        required: true
        description: frequency from [a, d, m, q]
      - name: start_date
        in: query
        type: string
        required: false
        description: start date.
      - name: end_date
        in: query
        type: string
        required: false
        description: end date.
      - name: format
        in: query
        type: string
        required: false
        description: csv or json
    responses:
        400:
            description: You have one the following errors. Wrong name or frequency.
                        start date in future or end_date greater than start_date
        200:
            description:  Json or Csv response of queried data with specified format.
   """

    args = RequestArgs()
    data = queries.select_datapoints(**args.query_param)
    if args.format == 'json':
        return publish_json(data)
    else:
        return publish_csv(data)        


def no_download(csv_str):
    return Response(response=csv_str, mimetype='text/plain')

        
def publish_csv(data):
    csv_str = utils.to_csv([row.serialized for row in data])
    return no_download(csv_str)

        
def publish_json(data):
    return jsonify([row.serialized for row in data])


@api.route('/frequencies', methods=['GET'])
def get_freq(freq):
    return jsonify(Allowed.frequencies())


@api.route('/names/<freq>', methods=['GET'])
def get_possible_names(freq):
    """
    Gets all possible names to a given freq
    ---
    tags:
        - name

    parameters:
      - name: freq
        in: path
        type: string
        required: true
        description: freq to get names for. Choose from [a, d, m, q]

    responses:
        200:
            description: Returns a list of names
    """
    possible_names = queries.possible_names_values(freq)
    return jsonify(possible_names)


@api.route('/info', methods=['GET'])
def get_date_range():
    """
    Gets a json with start_date and end_date of a give name and frequency pair
    ---
    tags:
        - info

    parameters:
        - name: name
          in: query
          type: string
          required: true
          description: the datapoint name
        - name: freq
          in: query
          type: string
          required: true
          description: frequency from [a, d, m, q]

    responses:
        400:
            description: Request lacks either freq or name argument or start_date greater than end_date.
        200:
            description: Returns a start_date and end_date json.

    """
    args = RequestArgs()    
    #NOT TODO YET: query on available frequencies + make frequency an optional parameter
    var, unit = label.split_label(args.name)
    result = dict(name = args.name,
                  var = {'id': var, 'en': 'reserved', 'ru': 'reserved'},
                  unit = {'id': unit, 'en': 'reserved', 'ru': 'reserved'}
                  )
    dr = queries.DateRange(freq=args.freq, name=args.name)
    result['frequencies'] = {args.freq: {'start_date': dr.min, 
                                         'latest_date': dr.max,
                                         'latest_value': 'reserved'}   
                            }
    return jsonify(result)

    
@api.route('/delete', methods=['DELETE'])
def delete_datapoints():
    """
    Deletes a datapoint based on it's name or units.
    ---
    tags:
        -delete
    parameters:
        -name: name
         in: query
         type: string
         required: false
         description: the datapoint name
        -unit: unit
         in: querry
         type:string
         required: false
         description: the unit of datapoint
    responses:
        403:
            description: Failed to authenticate correctly
        400:
            description: Request lacks either name or unit
            
    """
    #check identity
    token_to_check = request.args.get('API_TOKEN') or request.headers.get('API_TOKEN')
    if token_to_check != current_app.config['API_TOKEN']:
        return abort(403)
    #delete datapoints
    try:
        queries.delete(request.args.get('name'),request.args.get('unit'))
        return jsonify({})
    except ValueError:
        abort(400)

# api/dataframe?freq=a&name=GDP_yoy,CPI_rog&start_date=2013-12-31
@api.route('/dataframe', methods=['GET'])
def get_dataframe():
    args = RequestFrameArgs()
    param = args.query_param
    if not args.names:
         param['names'] = Allowed.names(args.freq)    
    data = queries.select_dataframe(**param)
    csv_str = utils.dataframe_to_csv(data, param['names'])
    return no_download(csv_str)