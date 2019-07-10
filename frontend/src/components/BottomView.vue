<template>
  <div style="display: flex;" v-show="showbottomview">
      
      <svg :id="svgid">
        <!-- <BottomView v-for="item in clusterList" v-bind:key="item" /> -->
      </svg>
  </div>
</template>

<script>
import * as d3 from 'd3'
import DataService from '../services/data-service'
import DrawService from '../services/draw-service'
import Transitionview from './Transition'
import { eventBus } from "../eventBus.js"
export default {
  name: 'BottomView',
  components: {
    // Transitionview
  },
  data () {
    return {
      svgid:"",
      clusterList:[1, 2, 3],
      showbottomview: false,
      low: 100,
      high: 300,  
      config: {
        disableZoom: false,
        scalesize: 4.2,
        problemid: "20x746187641c59c168",
        userid: '0474000000008137',
        svgid_set: [],
        cellRadius: 4,
        imagePath: 'image/20x746187641c59c168.jpg'
      },
    }
  },
  components: {
  },
  props: {

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
        this.showbottomview = true
        Object.getPrototypeOf(DataService).getUserSequenceByProblem.call(this, "renderBottoms", this.config)
      } else {
        this.showbottomview = false
      }
    })
  },
  methods: {
    renderBottoms (data) {
      let localsvg = d3.select('#'+ this.config.svgid_set.pop())
        .attr('class', 'bottom_SVG')
      // Keep score's type as Number and keep the latest score
      for (let i = 0; i < data.length; i++) {
          if (data[i]['score'].length > 0) {
              data[i]['score'][0] = parseInt(data[i]['score'][data[i]['score'].length - 1])
          }
      }
      let range = this.paceFilter(this.low, this.high, data)
      if (this.config.svgid_set.length == 0){
        Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, data, DataService.content.validSetCenter, this.config, false)
      }else{
        Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, data, DataService.content.validSetCenter, this.config, false)
      }
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