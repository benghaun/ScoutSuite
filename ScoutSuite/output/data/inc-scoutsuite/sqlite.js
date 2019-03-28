// Query separator, keeping it really short it will be used often, hence the truncated name
var qS = '¤'

// Keeping this for now for manual debugging, should be removed later on
function sqliteTest () {
  var request = new XMLHttpRequest()
  request.open('GET', 'http://127.0.0.1:8000/api/data?key=', true)

  request.onload = function () {
    var data = JSON.parse(this.response)
    console.log(data.data)
  }

  request.send()
}

// Example query : http://127.0.0.1:8000/api/data?key=last_run.time
function requestDb (query) {
  var request = new XMLHttpRequest()
  request.open('GET', 'http://127.0.0.1:8000/api/data?key=' + query, false)

  var response
  request.onload = function () {
    if (this.readyState === 4) {
      response = JSON.parse(this.response)
      if (response.data === null || response.data === undefined) {
        console.log('Error, bad request: ' + query)
      }
    }
  }

  request.send()
  return response.data
}

function getScoutsuiteResultsSqlite () {
  // The layers are named here in this fashion, these names don't always make sense depending in which
  // nested dict you are: paths(0), groups(1), services(2), counters(3), resources(4), items(5)
  let paths = requestDb('').keys
  run_results = {}
  for (let i in paths) { // Layer 0
    let list = {}
    let groups = requestDb(paths[i]) 
    if (groups.keys) {
      groups = groups.keys
    } else {
      run_results[paths[i]] = groups 
      continue
    }
    for (let group in groups) { // Layer 1
      list[groups[group]] = requestDb(paths[i] + qS + groups[group])
      let services = list[groups[group]].keys
      if (services) {        
        for (let service in services) { // Layer 2
          list[groups[group]][services[service]] = { [null] : null }
          let counters = requestDb(paths[i] + qS + groups[group] + qS + services[service])
          if (counters.keys) {
            counters = counters.keys
          } else {
            continue
          }              
          // The only elements for which we do not want to fetch everything are the resources which
          // are not filters or findings since they will scale with the environment's size
          if (paths[i] === 'services' && [services[service]] != 'filters' && [services[service]] != 'findings') {
            continue 
          }   
          for (let counter in counters) { // Layer 3
            list[groups[group]][services[service]][counters[counter]] = 
              requestDb(paths[i] + qS + groups[group] + qS + services[service] + qS + counters[counter])           
            let resources = list[groups[group]][services[service]][counters[counter]].keys              
            for (let resource in resources) { // Layer 4
              list[groups[group]][services[service]][counters[counter]][resources[resource]] = requestDb(paths[i] + qS + 
              groups[group] + qS + services[service] + qS + counters[counter] + qS + resources[resource])
              let items = list[groups[group]][services[service]][counters[counter]][resources[resource]].keys
              for (let item in items) { // Layer 5
                list[groups[group]][services[service]][counters[counter]][resources[resource]][items[item]] = 
                requestDb(paths[i] + qS + groups[group] + qS + services[service] + qS + counters[counter] + qS + 
                resources[resource] + qS + items[item])
                delete list[groups[group]][services[service]][counters[counter]].type
                delete list[groups[group]][services[service]][counters[counter]].keys
              }
            }
          }
          delete list[groups[group]][services[service]].null
        }
        delete list[groups[group]].type
        delete list[groups[group]].keys
      }
    }
    run_results[paths[i]] = list
  }
  console.log(run_results)
  return run_results
}

