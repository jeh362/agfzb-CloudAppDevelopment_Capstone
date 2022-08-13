/**
  *
  * main() will be run when you invoke this action
  *
  * @param Cloud Functions actions accept a single parameter, which must be a JSON object.
  *
  * @return The output of this action, which must be a JSON object.
  *
  */
 const Cloudant = require('@cloudant/cloudant');
  
  const credentials = {
      "COUCH_URL": '',
      "IAM_API_KEY": ''
  }
  
function main(params) {
    
    const cloudant = Cloudant({
        url: credentials.COUCH_URL,
        plugins: { iamauth: { iamApiKey: credentials.IAM_API_KEY } }
    });
    
    const Filter = params.state !== undefined ? {
        selector: { st: { "$eq": params.state.replace(/"/g, '') }, },
        fields: [ "id", "city", "state", "st", "address", "zip", "lat", "long", "short_name", "full_name" ]
    } : params.dealerId !== undefined ? {
        selector: { id: { "$eq": parseInt(params.dealerId) } },
        fields: [ "id", "city", "state", "st", "address", "zip", "lat", "long", "short_name", "full_name" ]
    } : {
        selector: { },
        fields: [ "id", "city", "state", "st", "address", "zip", "lat", "long", "short_name", "full_name" ]
    }
    
    
    let dbListPromise = get_dealerships(cloudant, Filter);
    
    return dbListPromise
}

function get_dealerships(cloudant, findO) {
    return new Promise((resolve, reject) => {
        cloudant.use('dealerships').find(findO)
            .then(resp => {
                resolve({ rows: resp.docs });
            })
            .catch(err => {
                reject({ err: err });
            });
    });   
}