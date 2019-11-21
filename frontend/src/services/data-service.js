class Service {
    constructor() {
        let content = {}
        content.serverIP = 'http://localhost:5003'
        content.serverUrl = `${this.serverIP}`
        content.data = {}
        content.validSetCenter = []
        content.validSetCenterSize = []
        content.baseFilterSet = {}
        this.content = content
        return this
    }
    getSequence(callback, config) {
        let that = this
        let xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                let x = xhr.responseText.replace(/'/g, '"')
                let data = JSON.parse(x)
                if (callback) {
                    that[callback](data.data)
                }
            }
        }
        xhr.open('get', 'http://127.0.0.1:5000/problemsequence?pid=' + config.problemid + '&userid=' + config.userid, true)
        xhr.send()
    }
    getOneSequence(callback, config) {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (callback) {
                    callback()
                }
            }
        }
        xhr.open('get', 'http://127.0.0.1:5000/usersequencebyuidpid?pid=' + config.problemid + '&userid=' + config.userid, true)
        xhr.send()
    }
    setImportantArea(baseFilterSet, config) {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('Area set success!')
            }
        }
        xhr.open('POST', 'http://127.0.0.1:5000/setimportantarea?pid=' + config.problemid + '&userid=' + config.userid, true)
        xhr.send(JSON.stringify({ 'data': baseFilterSet, 'scale': config.rectsize, 'config': config }))
    }
    getUserSequenceByProblem(callback, config) {
        let that = this
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                var x = xhr.responseText.replace(/'/g, '"')
                var data = JSON.parse(x)
                if (callback) {
                    that[callback](data.data)
                }
            }
        }
        xhr.open('get', 'http://127.0.0.1:5000/usersequencebyproblem?pid=' + config.problemid + '&userid=' + config.userid, true)
        xhr.send()
    }
    getClusterResultByProblem(callback, config) {
        let that = this
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                var x = xhr.responseText.replace(/'/g, '"')
                var data = JSON.parse(x)
                if (callback) {
                    that[callback]([data.data, data.fullSeq])
                }
            }
        }
        xhr.open('get', 'http://127.0.0.1:5000/clusterresultbyproblem?pid=' + config.problemid + '&userid=' + config.userid, true)
        xhr.send()
    }
    getproblemdetails(callback, config) {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                var x = xhr.responseText.replace(/'/g, '"')
                var data = JSON.parse(x)
                if (callback) {
                    callback(data.data)
                }
            }
        }
        xhr.open('get', 'http://127.0.0.1:5000/problemdetails?pid=' + config.problemid + '&userid=' + config.userid, true)
        xhr.send()
    }
    getImportantArea(callback, config) {
        let that = this
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                var x = xhr.responseText.replace(/'/g, '"')
                var data = {}
                try {
                    data = JSON.parse(x)
                } catch (error) {
                    console.log(error)
                }
                if (callback) {
                    that[callback](data)
                }
            }
        }
        xhr.open('get', 'http://127.0.0.1:5000/getimportantarea?pid=' + config.problemid + '&userid=' + config.userid, true)
        xhr.send()
    }
}

const DataService = new Service()
export default DataService