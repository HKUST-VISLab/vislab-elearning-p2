import * as d3 from 'd3'
class Service {
    // eslint-disable-next-line no-useless-constructor
    constructor() {

    }
    getColorByIndex(index) {
        let color = ['#00e2b6', '#f25d0c', '#0fac82', '#ac330f', '#36bce2', '#0f88ac', '#e06868', '#ff906a', '#f2db09', '#cae602', '#2e613b', '#7e6a7c', '#7fff8e', '#7fff8e', '#8397b3', '#ffe4c4']
        return color[index]
    }
    drawRect(localsvg, localdata, config) {
        let localg = localsvg.append('g')
        for (let key in localdata) {
            let x = parseInt(key.split('_')[0])
            let y = parseInt(key.split('_')[1])
            localg.append('rect')
                .attr('width', config.cellRadius)
                .attr('height', config.cellRadius)
                .attr('fill', this.getColorByIndex(localdata[key]))
                .attr('opacity', 0.7)
                .attr('transform', 'translate(' + (x * config.cellRadius) + ',' + (y * config.cellRadius) + ')')
        }
    }
    getImgUrl(picname) {
        return require('../assets/' + picname)
    }
    appendBackground(localsvg, config) {
        let localg = localsvg.append('g')
        localg.append('image')
            .attr('class', '.headimage')
            .attr('xlink:href', this.getImgUrl(config.imagePath))
            .attr('width', config.width)
            .attr('height', config.height)
            .attr('z-index', -1)
            .attr('x', 0)
            .attr('y', 0)
    }
    drawTraceOverview(svgNode, range, data, interestingPoints, dataconfig, lowscale) {
        // mapList: Store everyone's computed transition information
        let scalesize = dataconfig.scalesize
        let disableZoom = dataconfig.disableZoom
        if (lowscale) {
            scalesize = 1
            disableZoom = true
        }
        let cellRadius = dataconfig.cellRadius
        let localWidth = 960 / scalesize
        let localHeight = 600 / scalesize
        let minR = 10 / scalesize
        let maxR = 30 / scalesize
        let curRate = 30 / scalesize
        let maxBandwidth = maxR * 2
        let outWidth = 4 / scalesize
        let interestAreaListAll = []
        let mapList = []
        let timeSlice = 4
        let eventTypeNum = 3
        let color = ['#fdd0a2', '#fdae6b', '#f16913', '#d94801']
            // inerestNum: The number of interest points
        let interestNum = interestingPoints.length
        let xScale = d3.scaleLinear().domain([0, 960]).range([0, localWidth])
        let yScale = d3.scaleLinear().domain([0, 600]).range([0, localHeight])
        svgNode.selectAll('*').remove()
        svgNode.attr('width', localWidth)
            .attr('height', localHeight)
        let localg = svgNode.attr('class', 'main_view').append('g');
        if (lowscale) {
            localg.append('image')
                .attr('class', '.headimage')
                .attr('xlink:href', this.getImgUrl('image/' + dataconfig.problemid + '.jpg'))
                .attr('width', localWidth)
                .attr('height', localHeight)
                .attr('z-index', -1)
                .attr('x', 0)
                .attr('y', 0)
        }

        function _generateMap(pointsOrder, sequenceLength, intstPointNum) {
            let map = []
            for (let i = 0; i < intstPointNum; i++) {
                let oneLine = []
                for (let j = 0; j < intstPointNum; j++) {
                    let edge = {}
                    edge['weight'] = 0
                    edge['timeAll'] = []
                    oneLine.push(edge)
                }
                map.push(oneLine)
            }
            let time = 0
            for (let i = 0; i < sequenceLength - 1; i++) {
                let start = pointsOrder[i]
                let end = pointsOrder[i + 1]
                map[start][end].weight += 1 / sequenceLength
                map[start][end]['timeAll'].push(time)
                time++
            }
            // Get the most time period of each link
            for (let start = 0; start < intstPointNum; start++) {
                for (let end = 0; end < intstPointNum; end++) {
                    let temp = [0, 0, 0, 0]
                    for (let order = 0; order < map[start][end]['timeAll'].length; order++) {
                        temp[Math.floor(map[start][end]['timeAll'][order] / (sequenceLength / 4))] += 1
                        map[start][end]['timeAll'][order] = Math.floor(map[start][end]['timeAll'][order] / (sequenceLength / 4))
                    }
                    map[start][end]['time'] = _indexOfMax(temp)
                }
            }
            return map
        }

        function _indexOfMax(arr) {
            if (arr.length === 0) {
                return -1
            }
            let max = arr[0]
            let maxIndex = 0
            for (let i = 1; i < arr.length; i++) {
                if (arr[i] > max) {
                    maxIndex = i
                    max = arr[i]
                }
            }
            return maxIndex
        }

        function _curvPath(a, b, curv) {
            let x1 = a.x * cellRadius
            let x2 = b.x * cellRadius
            let y1 = a.y * cellRadius
            let y2 = b.y * cellRadius
            let s = 'M' + x1 + ',' + y1 + ' '
            let k2 = -(x2 - x1) / (y2 - y1)
            let controlX
            let controlY
            let path = ''
            if (k2 < 2 && k2 > -2) {
                controlX = (x2 + x1) / 2 + curv * curRate
                controlX = controlX < 0 ? -controlX : controlX
                controlY = k2 * (controlX - (x1 + x2) / 2) + (y1 + y2) / 2
                controlY = controlY < 0 ? -controlY : controlY
            } else {
                controlY = (y2 + y1) / 2 + curv * curRate
                controlY = controlY < 0 ? -controlY : controlY
                controlX = (controlY - (y1 + y2) / 2) / k2 + (x1 + x2) / 2
                controlX = controlX < 0 ? -controlX : controlX
            }
            let q = 'Q' + controlX + ',' + controlY + ' '
            let l = x2 + ',' + y2 + ' '
            path = s + q + l
            return path
        }

        function _zoomed() {
            // Create new scale ojects based on event
            let xScale = d3.scaleLinear().domain([0, window.outerWidth]).range([0, window.outerWidth])
            let yScale = d3.scaleLinear().domain([0, window.outerHeight]).range([0, window.outerHeight])
            let newxScale = d3.event.transform.rescaleX(xScale)
            let newyScale = d3.event.transform.rescaleY(yScale)
                // Update circle
            localg.selectAll('.transition_line').attr('transform', d3.event.transform)
            localg.selectAll('.arc').remove()
            localg.selectAll('.arc1').remove()
            localg.selectAll('#reset').remove();
            // Draw Transition Map's interest points
            for (let k = 0; k < interestNum; k++) {
                // Draw the time circle
                let path = d3.arc()
                    .outerRadius(interestAreaOverview[k].z === 0 ? 0 : rScale(interestAreaOverview[k].z))
                    .innerRadius(0)

                let pie = d3.pie()
                    .value(d => d)
                    .sort((a, b) => a)

                localg.selectAll('.main_view')
                    .data(pie(interestAreaOverview[k]['timeRatio']))
                    .enter()
                    .append('path')
                    .attr('class', 'arc')
                    .attr('d', path)
                    .attr('fill', function(d, i) {
                        return color[i]
                    })
                    .attr('stroke', 'black')
                    .attr('stroke-width', 0.1)
                    .attr('transform', 'translate(' + newxScale(interestAreaOverview[k].x * cellRadius) + ',' + newyScale(interestAreaOverview[k].y * cellRadius) + ')')

                // Draw the event circle
                let path1 = d3.arc()
                    .outerRadius(interestAreaOverview[k].z === 0 ? 0 : rScale(interestAreaOverview[k].z) + 4)
                    .innerRadius(interestAreaOverview[k].z === 0 ? 0 : rScale(interestAreaOverview[k].z))

                let color1 = ['black', 'whitesmoke', 'gray']
                localg.selectAll('.main_view')
                    .data(pie(interestAreaOverview[k]['eventType']))
                    .enter()
                    .append('path')
                    .attr('class', 'arc1')
                    .attr('transform', 'translate(' + newxScale(interestAreaOverview[k].x * cellRadius) + ',' + newyScale(interestAreaOverview[k].y * cellRadius) + ')')
                    .attr('d', path1)
                    .attr('fill', function(d, i) {
                        return color1[i]
                    })
            }
            // Add reset button
            // localg.append('rect')
            //   .attr('id', 'reset')
            //   .attr('transform', 'translate(' + (localWidth - 100) + ',' + (localHeight - 50) + ')')
            //   .attr('width', 80)
            //   .attr('height', 30)
            //   .style('fill', 'grey')
            //   .attr('display', 'block')
            // localg.append('text')
            //   .attr('id', 'reset')
            //   .text('Reset')
            //   .attr('fill', 'white')
            //   .attr('font-size', 25)
            //   .attr('x', localWidth - 88)
            //   .attr('y', localHeight - 27)
            // d3.selectAll('#reset').on('click', () => {
            //   DrawService.drawTraceOverview(svgNode, range, interestingPoints, data, dataconfig)
            // })
        }

        function _noname(eventType, pointsOrder, sequenceLength) {
            let interestAreaList = []
            for (let i = 0; i < interestNum; i++) {
                let interestArea = {}
                interestArea['x'] = xScale(Number(interestingPoints[i][0] * cellRadius))
                interestArea['y'] = yScale(Number(interestingPoints[i][1] * cellRadius))
                interestArea['z'] = 0
                interestArea['eventType'] = Array(timeSlice).fill(0)
                interestArea['timeRatio'] = Array(eventTypeNum).fill(0)
                interestAreaList.push(interestArea)
            }
            for (let i = 0; i < sequenceLength; i++) {
                interestAreaList[pointsOrder[i]].z += 1 / sequenceLength
            }
            // Calculate the time ratio of each interest point
            for (let i = 0; i < sequenceLength; i++) {
                for (let j = 0; j < timeSlice; j++) {
                    if (i >= Math.ceil(j * sequenceLength / timeSlice) && i <= Math.floor((j + 1) * sequenceLength / timeSlice)) {
                        interestAreaList[pointsOrder[i]]['timeRatio'][j] += 1 / sequenceLength
                    }
                }
            }
            // Calculate the action number on each interest point
            // for (let i = 0; i < sequenceLength; i++) {
            //   interestAreaList[pointsOrder[i]].z += 1 / sequenceLength
            //   for (let j = 0; j < timeSlice; j++) {
            //     if (i >= Math.ceil(j * sequenceLength / timeSlice) && i <= Math.floor((j + 1) * sequenceLength / timeSlice)) {
            //       interestAreaList[pointsOrder[i]]['timeRatio'][j] += 1 / sequenceLength
            //     }
            //   }
            // }
            for (let i = 0; i < sequenceLength; i++) {
                if (eventType[i] === 'mouseup') {
                    interestAreaList[pointsOrder[i]]['eventType'][0] += 1 / sequenceLength
                }
                if (eventType[i] === 'mousedown') {
                    interestAreaList[pointsOrder[i]]['eventType'][1] += 1 / sequenceLength
                }
                if (eventType[i] === 'mousemove') {
                    interestAreaList[pointsOrder[i]]['eventType'][2] += 1 / sequenceLength
                }
            }
            return interestAreaList
        }
        for (let q = 0; q < range.length; q++) {
            let k = range[q] // k: The order number in data
            let eventType = data[k]['eventtypes'] // eventType: The event type order sequence
            let pointsOrder = data[k]['states'] // pointsOrder: The order sequence of interest points
            let sequenceLength = pointsOrder.length
            interestAreaListAll.push(_noname(eventType, pointsOrder, sequenceLength))
                // Calculate the link information between points
            mapList.push(_generateMap(pointsOrder, sequenceLength, interestNum))
        }
        // mapOverview: add all users' sequence information up
        let mapOverview = Array(interestNum).fill().map(() => { return Array(interestNum).fill().map(() => { return { weight: 0, time: -1, timeAll: [] } }) })
        for (let k = 0; k < mapList.length; k++) {
            mapOverview.map((d1, i) => {
                d1.map((d2, j) => {
                    d2['weight'] += mapList[k][i][j]['weight']
                    d2['timeAll'] = d2['timeAll'].concat(mapList[k][i][j]['timeAll'])
                })
            })
        }
        // Initial the interestAreaOverview parameters
        let interestAreaOverview = []
        for (let i = 0; i < interestNum; i++) {
            let interestArea = {}
            interestArea['x'] = xScale(interestingPoints[i][0])
            interestArea['y'] = yScale(interestingPoints[i][1])
            interestArea['z'] = 0
            interestArea['eventType'] = Array(timeSlice).fill(0)
            interestArea['timeRatio'] = Array(eventTypeNum).fill(0)
            interestAreaOverview.push(interestArea)
        }
        // Get the most time period of each link
        for (let i = 0; i < interestNum; i++) {
            for (let j = 0; j < interestNum; j++) {
                let temp = [0, 0, 0, 0]
                for (let order = 0; order < mapOverview[i][j]['timeAll'].length; order++) {
                    if (mapOverview[i][j]['timeAll'][order] !== -1) {
                        temp[mapOverview[i][j]['timeAll'][order]] += 1
                    }
                }
                mapOverview[i][j]['time'] = _indexOfMax(temp)
            }
        }
        // Calculate the action ratio on each interest point
        for (let i = 0; i < interestAreaListAll.length; i++) {
            for (let j = 0; j < interestNum; j++) {
                interestAreaOverview[j]['z'] += interestAreaListAll[i][j]['z']
                for (let k = 0; k < timeSlice; k++) {
                    interestAreaOverview[j]['timeRatio'][k] += interestAreaListAll[i][j]['timeRatio'][k]
                }
                for (let v = 0; v < eventTypeNum; v++) {
                    interestAreaOverview[j]['eventType'][v] += interestAreaListAll[i][j]['eventType'][v]
                }
            }
        }
        // maxWeight: get the max link weight
        let maxWeight = Math.max(...mapOverview.map((d, i) => { return Math.max(...d.map((wt) => wt.weight)) }))
            // Limit the max size of interest points
        let rScale = d3.scaleSqrt().domain(d3.extent(interestAreaOverview, d => d.z)).range([minR, maxR])
            // Limit the max width of transition line
        let swScale = d3.scaleLinear().domain([0, maxWeight]).range([0, maxBandwidth])
            // Add zoom function in the view
            // Append zoom area
        if (!disableZoom) {
            let zoom = d3.zoom().on('zoom', _zoomed)
            localg.append('rect')
                .attr('class', 'zoom')
                .style('fill', 'white')
                .attr('opacity', 0.1)
                .attr('width', localWidth)
                .attr('height', localHeight)
                .call(zoom)

            // localg.append('image')
            //     .attr('class', 'zoom')
            //     .call(zoom)
            //     .attr('xlink:href', '../static/img/20x746187641c59c168.jpg')
            //     .attr('width', localWidth)
            //     .attr('height', localHeight)

        }
        // Draw Transition Map's line
        for (let i = 0; i < interestNum; i++) {
            for (let j = 0; j < interestNum; j++) {
                // draw path
                if (i !== j) {
                    let path = _curvPath(interestAreaOverview[i], interestAreaOverview[j], 5 * (1 - swScale(mapOverview[i][j].weight) / swScale(maxWeight)))
                    localg.append('path').attr('d', path)
                        .attr('class', 'transition_line')
                        .attr('fill', 'none')
                        .attr('stroke', color[mapOverview[i][j].time])
                        .attr('stroke-width', swScale(mapOverview[i][j].weight))
                        .attr('opacity', 0.5)
                }
            }
        }
        // Draw Transition Map's interest points
        for (let k = 0; k < interestNum; k++) {
            // Draw the time circle
            let path = d3.arc()
                .outerRadius(interestAreaOverview[k].z === 0 ? 0 : rScale(interestAreaOverview[k].z))
                .innerRadius(0)

            let pie = d3.pie()
                .value(d => d)
                .sort((a, b) => a)

            localg.selectAll('.main_view')
                .data(pie(interestAreaOverview[k]['timeRatio']))
                .enter()
                .append('path')
                .attr('class', 'arc')
                .attr('d', path)
                .attr('fill', (d, i) => color[i])
                .attr('stroke', 'black')
                .attr('stroke-width', 0.1)
                .attr('transform', 'translate(' + (interestAreaOverview[k].x * cellRadius) + ',' + (interestAreaOverview[k].y * cellRadius) + ')')

            // Draw the event circle
            let path1 = d3.arc()
                .outerRadius(interestAreaOverview[k].z === 0 ? 0 : rScale(interestAreaOverview[k].z) + outWidth)
                .innerRadius(interestAreaOverview[k].z === 0 ? 0 : rScale(interestAreaOverview[k].z))

            let color1 = ['black', 'whitesmoke', 'gray']
            localg.selectAll('.main_view')
                .data(pie(interestAreaOverview[k]['eventType']))
                .enter()
                .append('path')
                .attr('class', 'arc1')
                .attr('transform', 'translate(' + (interestAreaOverview[k].x * cellRadius) + ',' + (interestAreaOverview[k].y * cellRadius) + ')')
                .attr('d', path1)
                .attr('fill', (d, i) => color1[i])
        }
    }

    drawchart(data, localsvg, config) {
        let daHeight = config.height;
        let daWidth = config.width;
        localsvg.selectAll('*').remove();
        let margin = { left: 40, top: 18, right: 20, bottom: 27 };
        // let tdXScale = d3.scaleBand().range([0, daWidth - margin.left - margin.right]).padding(0.1);
        // let tdYScale = d3.scaleLinear().range([daHeight / 2 - margin.bottom - margin.top, 0]);
        let adXScale = d3.scaleBand().range([0, daWidth - margin.left - margin.right]).padding(0.1);
        let adYScale = d3.scaleLinear().range([daHeight / 2 - margin.bottom - margin.top, 0]);
        let sdXScale = d3.scaleBand().range([0, daWidth - margin.left - margin.right]).padding(0.1);
        let sdYScale = d3.scaleLinear().range([daHeight - margin.bottom, daHeight / 2 + margin.top]);
        let timeCal = _timeDistribution(_timeinfoRepos(data));
        let scoreCal = _scoreDistribution(_scoreinfoRepos(data));
        let actionCal = _actionDistribution(_actioninfoRepos(data));
        // Build repository to store the data needed
        function _timeinfoRepos(data) {
            let timeRep = []
            for (let i = 0; i < data.length; i++) {
                let tmp = {}
                tmp['userid'] = data[i].userid
                tmp['time_cost'] = (Number(data[i]['maxt']) - Number(data[i]['mint'])) / (1000 * 60)
                timeRep.push(tmp)
            }
            return timeRep
        }

        function _scoreinfoRepos(data) {
            let scoreRep = []
            for (let j = 0; j < data.length; j++) {
                let tmp = {}
                tmp['userid'] = data[j].userid
                tmp['score'] = Math.random() * 100
                scoreRep.push(tmp)
            }
            return scoreRep
        }

        function _actioninfoRepos(data) {
            let actionRep = [];
            for (let k = 0; k < data.length; k++) {
                let tmp = {};
                let actionCount = 0;
                tmp['userid'] = data[k].userid;
                for (let i = 0; i < data[k].eventtypes.length; i++) {
                    if (data[k].eventtypes[i] == 'mousedown') {
                        actionCount++;
                    }
                }
                tmp['action'] = actionCount;
                actionRep.push(tmp);
            }
            return actionRep;
        }
        // Calculate the time/score distribution
        function _timeDistribution(timeRep) {
            let timeCal = [
                ['<1min', 0],
                ['1~2min', 0],
                ['2~4min', 0],
                ['4~8min', 0],
                ['>8min', 0]
            ]
            for (let i = 0; i < timeRep.length; i++) {
                if (Number(timeRep[i].time_cost) <= 1) {
                    timeCal[0][1]++
                } else if (Number(timeRep[i].time_cost) > 1 && Number(timeRep[i].time_cost) <= 2) {
                    timeCal[1][1]++
                } else if (Number(timeRep[i].time_cost) > 2 && Number(timeRep[i].time_cost) <= 4) {
                    timeCal[2][1]++
                } else if (Number(timeRep[i].time_cost) > 4 && Number(timeRep[i].time_cost) <= 8) {
                    timeCal[3][1]++
                } else {
                    timeCal[4][1]++
                }
            };
            return timeCal
        };

        function _scoreDistribution(scoreRep) {
            let scoreCal = [
                ['0~24', 0],
                ['25~49', 0],
                ['50~74', 0],
                ['75~100', 0]
            ]
            for (let i = 0; i < scoreRep.length; i++) {
                if (Number(scoreRep[i].score) <= 24) {
                    scoreCal[0][1]++
                } else if (Number(scoreRep[i].score) > 24 && Number(scoreRep[i].score) <= 49) {
                    scoreCal[1][1]++
                } else if (Number(scoreRep[i].score) > 49 && Number(scoreRep[i].score) <= 74) {
                    scoreCal[2][1]++
                } else if (Number(scoreRep[i].score) > 74 && Number(scoreRep[i].score) <= 100) {
                    scoreCal[3][1]++
                }
            };
            return scoreCal
        };

        function _actionDistribution(actionRep) {
            // let actionMean = 0;
            // let actionVariance = 0;
            // for (let j = 0; j < actionRep.length; j++) {
            //     actionMean = +actionRep[j].action;
            //     actionVariance = +Math.pow(actionRep[j].action, 2)
            // };
            // actionMean = actionMean / actionRep.length;
            // actionVariance = (actionVariance - Math.pow(actionMean, 2)) / actionRep.length;
            // for (let k = 0; k < actionRep.length; j++) {
            //     let yNDistribution = 0;
            //     yNDistribution = Math.exp(-Math.pow(actionRep[k].action - actionMean, 2) / (2 * actionVariance)) / Math.pow(2 * Math.PI * actionVariance, 1 / 2);
            //     actionRep[k].x = actionRep[k].action - actionMean;
            //     actionRep[k].y = yNDistribution
            // }
            let actionCal = [
                ['0~20', 0],
                ['21~40', 0],
                ['41~60', 0],
                ['61~80', 0],
                ['81~100', 0],
                ['>100', 0]
            ]
            for (let i = 0; i < actionRep.length; i++) {
                if (Number(actionRep[i].action) <= 20) {
                    actionCal[0][1]++
                } else if (Number(actionRep[i].action) > 20 && Number(actionRep[i].action) <= 40) {
                    actionCal[1][1]++
                } else if (Number(actionRep[i].action) > 40 && Number(actionRep[i].action) <= 60) {
                    actionCal[2][1]++
                } else if (Number(actionRep[i].action) > 60 && Number(actionRep[i].action) <= 80) {
                    actionCal[3][1]++
                } else if (Number(actionRep[i].action) > 80 && Number(actionRep[i].action) <= 100) {
                    actionCal[4][1]++
                } else {
                    actionCal[5][1]++
                }
            };
            return actionCal;
        }
        // Append axis
        // tdXScale.domain(timeCal.map(function(d) {
        //     return d[0]
        // }))
        // tdYScale.domain([0, d3.max(timeCal, function(d) {
        //     return d[1]
        // })])
        // localsvg.append('g')
        //     .attr('transform', 'translate(' + margin.left + ',' + (daHeight / 2 - margin.bottom) + ')')
        //     .call(d3.axisBottom(tdXScale))
        // localsvg.append('g')
        //     .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        //     .call(d3.axisLeft(tdYScale).ticks(6))
        adXScale.domain(actionCal.map(function(d) {
            return d[0]
        }))
        adYScale.domain([0, d3.max(actionCal, function(d) {
            return d[1]
        })])
        localsvg.append('g')
            .attr('transform', 'translate(' + margin.left + ',' + (daHeight / 2 - margin.bottom) + ')')
            .call(d3.axisBottom(adXScale))
        localsvg.append('g')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
            .call(d3.axisLeft(adYScale).ticks(6))
        sdXScale.domain(scoreCal.map(function(d) {
            return d[0]
        }))
        sdYScale.domain([0, d3.max(scoreCal, function(d) {
            return d[1]
        })])
        localsvg.append('g')
            .attr('transform', 'translate(' + margin.left + ',' + (daHeight - margin.bottom) + ')')
            .call(d3.axisBottom(sdXScale))
        localsvg.append('g')
            .attr('transform', 'translate(' + margin.left + ',0)')
            .call(d3.axisLeft(sdYScale).ticks(6));
        // Append axis label
        // localsvg.append('text')
        //     .attr('transform', 'translate(' + daWidth / 2 + ',' + margin.top + ')')
        //     .attr('text-anchor', 'middle')
        //     .attr('class', 'chart')
        //     .style('font-size', '22')
        //     .text('Time Distribution')
        // localsvg.append('text')
        //     .attr('transform', 'translate(' + margin.left * 0.38 + ',' + daHeight / 4 + '), rotate(-90)')
        //     .attr('class', 'chart')
        //     .style('font-size', '18')
        //     .attr('text-anchor', 'middle')
        //     .text('User Number')
        localsvg.append('text')
            .attr('transform', 'translate(' + daWidth / 2 + ',' + margin.top + ')')
            .attr('text-anchor', 'middle')
            .attr('class', 'chart')
            .style('font-size', '22')
            .text('Action Distribution')
        localsvg.append('text')
            .attr('transform', 'translate(' + margin.left * 0.38 + ',' + daHeight / 4 + '), rotate(-90)')
            .attr('class', 'chart')
            .style('font-size', '18')
            .attr('text-anchor', 'middle')
            .text('User Number')
        localsvg.append('text')
            .attr('transform', 'translate(' + daWidth / 2 + ',' + (margin.top + daHeight / 2) + ')')
            .attr('text-anchor', 'middle')
            .attr('class', 'chart')
            .style('font-size', '22')
            .text('Score Distribution')
        localsvg.append('text')
            .attr('transform', 'translate(' + margin.left * 0.38 + ',' + daHeight * 3 / 4 + '), rotate(-90)')
            .attr('class', 'chart')
            .style('font-size', '18')
            .attr('text-anchor', 'middle')
            .text('User Number');
        // Append the rectangles for the bar chart
        // localsvg.selectAll('.TD_bar')
        //     .data(timeCal)
        //     .enter().append('rect')
        //     .attr('class', 'TD_bar')
        //     .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        //     .attr('x', function(d) { return tdXScale(d[0]) })
        //     .attr('width', tdXScale.bandwidth())
        //     .attr('y', function(d) { return tdYScale(d[1]) })
        //     .attr('height', function(d) { return daHeight / 2 - margin.bottom - margin.top - tdYScale(d[1]) })
        //     .attr('fill', 'rgba(188,195,212)')
        localsvg.selectAll('.AD_bar')
            .data(actionCal)
            .enter().append('rect')
            .attr('class', 'AD_bar')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
            .attr('x', function(d) { return adXScale(d[0]) })
            .attr('width', adXScale.bandwidth())
            .attr('y', function(d) { return adYScale(d[1]) })
            .attr('height', function(d) { return daHeight / 2 - margin.bottom - margin.top - adYScale(d[1]) })
            .attr('fill', 'rgba(188,195,212)')
        localsvg.selectAll('.SD_bar')
            .data(scoreCal)
            .enter().append('rect')
            .attr('class', 'SD_bar')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
            .attr('x', function(d) { return sdXScale(d[0]) })
            .attr('width', sdXScale.bandwidth())
            .attr('y', function(d) { return sdYScale(d[1]) })
            .attr('height', function(d) { return daHeight - margin.bottom - margin.top - sdYScale(d[1]) })
            .attr('fill', 'rgba(188,195,212)')
    }
}
const DrawService = new Service()
export default DrawService