<template>
  <div>
    <div class = "content" id = "id_ROIview" v-show="showroiview">
      <svg id="id_roisvg" ></svg>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import SidePanel from './sidePanel'
import DataService from '../services/data-service'
import DrawService from '../services/draw-service'
import { eventBus } from "../eventBus.js"
export default {
  name: 'ROIview',
  data () {
    return {
      showroiview: true,
      width: 960,
      height: 600,
      mode: false,
      config: {
        problemid: "20x746187641c59c168",
        userid: '0474000000008137',
        width: 960,
        height: 600,
        cellRadius: 4,
        cellCoef: 13,
        upperThresh: 209/1000.0,
        lowerThresh: 200/1000.0,
        imagePath: 'image/20x746187641c59c168.jpg'
      },
    }
  },
  props: {
    cellRadius: {
      type: Number,
      required: true,
    },
    cellCoef: {
      type: Number,
      required: true,
    },
    upperThresh: {
      type: Number,
      required: true,
    },
    lowerThresh: {
      type: Number,
      required: true,
    },
    problemid: {
      required: true,
    }
  },
  watch: {
  },
  components: {
  },
  mounted () {
    eventBus.$on("changeProb", arr => {
      this.config.problemid = arr[0]
      this.config.cellRadius = arr[1]
      this.config.cellCoef = arr[2]
      this.config.upperThresh = arr[3]/1000.0
      this.config.lowerThresh = arr[4]/1000.0
      this.config.imagePath = 'image/' + this.config.problemid + '.jpg'
      Object.getPrototypeOf(DataService).getSequence.call(this, 'renderSVG', this.config)
    })
    eventBus.$on("roi_valuechange", arr => {
      this.config.problemid = arr[0]
      this.config.cellRadius = arr[1]
      this.config.cellCoef = arr[2]
      this.config.upperThresh = arr[3]/1000.0
      this.config.lowerThresh = arr[4]/1000.0
      this.config.imagePath = 'image/' + this.config.problemid + '.jpg'
      Object.getPrototypeOf(DataService).getSequence.call(this, 'renderSVG', this.config)
    })
    eventBus.$on("view_change", chosenview => {
      if(chosenview == 'roiview') {
        this.showroiview = true
      } else {
        this.showroiview = false
      }
    })
    eventBus.$on("mode_change", mode => {
      this.mode = mode
      Object.getPrototypeOf(DataService).getSequence.call(this, 'renderSVG', this.config)
    })
  },
  methods: {
    renderSVG (data) { 
      let localsvg = d3.select('#id_roisvg')
        .attr('class', 'd3SVG')
        .attr('width', this.width)
        .attr('height', this.height)

      let gaussData = this.gaussFilter(this.config.cellCoef, data)
      let rectarr = this.rawToBox(this.config.cellRadius, gaussData)
      let filterSet = this.detectObject(this.selectValid(this.config.upperThresh, rectarr))
      Object.getPrototypeOf(DrawService).appendBackground(localsvg, this.config)
      
      if (this.mode === 'true') {
        let baseFilterSet = {}
        baseFilterSet = this.selectValid(this.config.lowerThresh, rectarr)
        console.log(baseFilterSet)
        for (let key in baseFilterSet) {
          baseFilterSet[key] = this.minCenterDistance(key)
        }
        this.countObjectSize(baseFilterSet)
        Object.getPrototypeOf(DataService).setImportantArea(baseFilterSet, this.config)
        Object.getPrototypeOf(DrawService).drawRect(localsvg, baseFilterSet, this.config)
      } else {
        Object.getPrototypeOf(DrawService).drawRect(localsvg, filterSet, this.config)
      }
    },
    countObjectSize (baseFilterSet) {
      let localmax = 0
      for (let key in baseFilterSet) {
        if (baseFilterSet[key] > localmax) {
          localmax = baseFilterSet[key]
        }
      }
      DataService.content.validSetCenterSize = new Array(localmax).fill(0)
      for (let key in baseFilterSet) {
        DataService.content.validSetCenterSize[baseFilterSet[key]]++
      }
    },
    minCenterDistance (key) {
      let x = parseInt(key.split('_')[0])
      let y = parseInt(key.split('_')[1])
      let localmin = 100000000
      let index = 0
      for (let i = 0; i < DataService.content.validSetCenter.length; i++) {
        let tmp = Math.pow((x - DataService.content.validSetCenter[i][0]), 2) + Math.pow((y - DataService.content.validSetCenter[i][1]), 2)
        if (tmp < localmin) {
          localmin = tmp
          index = i
        }
      }
      return index
    },
    detectObject (filterSet) {
      DataService.content.validSetCenter = []
      let dealed = {}
      let index = 0
      function recuDetect (sideset, currentSector, localindex) {
        for (let i = 0; i < sideset.length; i++) {
          if (filterSet[sideset[i]] !== undefined && !currentSector[sideset[i]]) {
            dealed[sideset[i]] = localindex
            currentSector[sideset[i]] = 1
            let x = parseInt(sideset[i].split('_')[0])
            let y = parseInt(sideset[i].split('_')[1])
            let points = [(x - 1) + '_' + (y - 1), (x) + '_' + (y - 1), (x + 1) + '_' + (y - 1), (x - 1) + '_' + (y), (x + 1) + '_' + (y), (x - 1) + '_' + (y + 1), (x) + '_' + (y + 1), (x + 1) + '_' + (y + 1)]
            recuDetect(points, currentSector, localindex)
          }
        }
      }

      for (let key in filterSet) {
        if (dealed[key] === undefined) {
          let currentSector = {}
          let sumx = 0
          let sumy = 0
          recuDetect([key], currentSector, index)
          let curlen = Object.keys(currentSector).length
          if (curlen > 5) {
            for (let key in currentSector) {
              sumx += parseInt(key.split('_')[0])
              sumy += parseInt(key.split('_')[1])
            }
            DataService.content.validSetCenter.push([sumx / parseFloat(curlen), sumy / parseFloat(curlen)])
            index++
          }
        }
      }
      return dealed
    },
    rawToBox (rectsize, data) {
      let rectData = []
      let wi = data.length / rectsize
      let hi = data[0].length / rectsize
      for (let i = 0; i < wi; i++) {
        let tmp = []
        for (let t = 0; t < hi; t++) {
          let sm = 0
          let basex = i * rectsize
          let basey = t * rectsize
          for (let x = 0; x < rectsize; x++) {
            for (let y = 0; y < rectsize; y++) {
              try {
                sm += data[x + basex][y + basey]
              } catch (e) {
              }
            }
          }
          tmp.push(sm)
        }
        rectData.push(tmp)
      }
      return this.normalize(rectData)
    },
    normalize (arr) {
      let maxvalue = 0
      for (let i = 0; i < arr.length; i++) {
        for (let t = 0; t < arr[0].length; t++) {
          if (arr[i][t] > maxvalue) {
            maxvalue = arr[i][t]
          }
        }
      }
      for (let i = 0; i < arr.length; i++) {
        for (let t = 0; t < arr[i].length; t++) {
          arr[i][t] = arr[i][t] / parseFloat(maxvalue)
        }
      }
      return arr
    },
    selectValid (threshold, arr) {
      let localset = {}
      for (let i = 0; i < arr.length; i++) {
        for (let t = 0; t < arr[i].length; t++) {
          if (arr[i][t] >= threshold) {
            localset[i + '_' + t] = 1
          }
        }
      }
      return localset
    },
    gaussFilter (blursize, arr) {
      let newarr = []
      let blursqr = parseFloat(blursize * blursize)
      for (let i = 0; i < arr.length; i++) {
        let tmp = []
        for (let t = 0; t < arr[i].length; t++) {
          let avg = arr[i][t]
          for (let x = i - blursize; x < i + blursize; x++) {
            for (let y = t - blursize; y < t + blursize; y++) {
              if (x >= 0 && y >= 0 && x < arr.length && y < arr[i].length) {
                avg += arr[x][y]
              }
            }
          }
          tmp.push(avg / blursqr)
        }
        newarr.push(tmp)
      }
      return newarr
    }
  }
}
</script>