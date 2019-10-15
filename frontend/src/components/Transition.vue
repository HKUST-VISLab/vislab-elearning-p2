<template>
  <div>
      <svg :id="svgid" v-show="showtransitionview"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3'
import SidePanel from './sidePanel'
import DrawService from '../services/draw-service'
import DataService from '../services/data-service'
import { eventBus } from "../eventBus.js"
export default {
  name: 'Transitionview',
  data () {
    return {
      svgid:"",
      showtransitionview: false,
      low: 100,
      high: 300,  
      config: {
        disableZoom: false,
        scalesize: 4.2,
        problemid: "20x746187641c59c168",
        userid: '0474000000008137',
        svgid_set: [],
        cellRadius: 4,
        maxRadius: this.maxRadius,
        minRadius: this.minRadius,
        imagePath: 'image/20x746187641c59c168.jpg'
      },
    }
  },
  props: {
    maxRadius: {
      type: Number,
      required: true
    },
    minRadius: {
      type: Number,
      required: true
    }
  },
  watch: {
    maxRadius(newValue, oldValue) {
        this.maxRadius = newValue
        this.config.maxRadius = this.maxRadius
        Object.getPrototypeOf(DataService).getUserSequenceByProblem.call(this, "renderTransition", this.config)
    },
    minRadius(newValue, oldValue) {
        this.minRadius = newValue
        this.config.minRadius = this.minRadius
        Object.getPrototypeOf(DataService).getUserSequenceByProblem.call(this, "renderTransition", this.config)
    },
  },
  components: {

  },
  mounted () {
    eventBus.$on("changeProb", arr => {
      this.svgid = "id" + parseInt(Math.random() * 100000)
      this.config.svgid_set.push(this.svgid)
      this.config.cellRadius = arr[1]
      this.config.problemid = arr[0]
      this.config.imagePath = 'image/' + this.config.problemid + '.jpg'
    })
    eventBus.$on("view_change", chosenview => {
      if(chosenview == 'transitionview') {
        this.showtransitionview = true
        Object.getPrototypeOf(DataService).getUserSequenceByProblem.call(this, "renderTransition", this.config)
      } else {
        this.showtransitionview = false
      }
    })
  },
  methods: {
    renderTransition (data) {
      let localsvg = d3.select('#'+ this.config.svgid_set[this.config.svgid_set.length-1])
        .attr('class', 'd3SVG')

      // Keep score's type as Number and keep the latest score
      for (let i = 0; i < data.length; i++) {
          if (data[i]['score'].length > 0) {
              data[i]['score'][0] = parseInt(data[i]['score'][data[i]['score'].length - 1])
          }
      }
      let range = this.paceFilter(this.low, this.high, data)
      if (this.config.svgid_set.length == 0){
        Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, data, DataService.content.validSetCenter, this.config, true)
      }else{
        Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, data, DataService.content.validSetCenter, this.config, true)
      }
    },
    scoreFilter (low, high, data) {
      let range = []
      for (let i = 0; i < data.length; i++) {
        if (data[i]['score'].length == 1) {
          if (data[i]['score'][0] >= low && data[i]['score'][0] <= high) {
            range.push(i)
          }
        }
      }
      return range
    },
    paceFilter (slow, fast, data) {
      let range = []
      let minStep = d3.min(data, function(d, i) {
        return d['states'].length
      })
      let maxStep = d3.max(data, function(d, i) {
        return d['states'].length
      })
      for (let i = 0; i < data.length; i++) {
        if (data[i]['states'].length >= 2) {
          if (data[i]['states'].length >= slow && data[i]['states'].length <= fast) {
            range.push(i)
          }
        }
      }
      return range
    }
  }
}
</script>