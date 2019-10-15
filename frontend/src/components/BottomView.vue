<template>
  <div style="overflow-y:hidden;" v-show="showbottomview">
      <div class = "content" id = "bottomview_div" style = "height: 100% ; width: 960px;"></div>
      <!-- <svg id="bottomview_svg"> -->
        <!-- <BottomView v-for="item in clusterList" v-bind:key="item" /> -->
      <!-- </svg> -->
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
      low: 10,
      high: 500,  
      config: {
        disableZoom: true,
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
      let orderNum = 0;
      // test variable
      let secondOrderNum = 0;
      let slicePartition = 5;
      // -------------
      let textSize = 18;
      let mapGap = 320;
      let textGap = 205;
      let validCount = 0;

      for (let i = 0; i < data.length; i++) {
        if (data[i]['score'].length > 0 && data[i]['score'][data[i]['score'].length - 1] == '100') {
          validCount ++;
        }
      }

      d3.select('#bottomview_div').selectAll('*').remove()
      let mainSVG = d3.select('#bottomview_div')
            .append('svg')
            .attr("id", "bottomview_svg")
            .attr('width', validCount * mapGap)
            .attr('height', 150 + 140);
      console.log(data)
      for (let i = 0; i < data.length; i++) {
        if (data[i]['score'].length > 0 && data[i]['score'][data[i]['score'].length - 1] == '100') {
          let currentScore = parseInt(data[i]['score'][data[i]['score'].length - 1])
          // Keep score's type as Number and keep the latest score
          data[i]['score'][0] = parseInt(data[i]['score'][data[i]['score'].length - 1])
          // test for trace slicing
          let currentActNum = parseInt(data[i]['states'].length/3)
          // ----------------------
          let currentUserid = data[i]['userid'].slice(11);
            
          let localsvg = mainSVG.append('g')
            .attr("id", "user" + i)
            .attr("transform", "translate(" + mapGap * orderNum + ", 0)")

          d3.select('#bottomview_svg').append('text')
            .attr("x", textGap + mapGap * orderNum)
            .attr("y", 60)
            .text("User ID:" + currentUserid)
            .attr("class", "textselected")
            .style("text-anchor", "start")
            .style("font-size", textSize)
          d3.select('#bottomview_svg').append('text')
            .attr("x", textGap + mapGap * orderNum)
            .attr("y", 80)
            .text("Score:" + currentScore)
            .attr("class", "textselected")
            .style("text-anchor", "start")
            .style("font-size", textSize)
          d3.select('#bottomview_svg')
            .append("line")
            .attr("x1", mapGap * (orderNum + 1))
            .attr("y1", 0)
            .attr("x2", mapGap * (orderNum + 1))
            .attr("y2", 140)
            .attr("stroke", "grey")
            .attr("stroke-width", "2px")
            .attr('opacity', 0.5);
          // test for trace slicing
          d3.select('#bottomview_svg').append('text')
            .attr("x", textGap + mapGap * orderNum)
            .attr("y", 100)
            .text("ActNum:" + currentActNum)
            .attr("class", "textselected")
            .style("text-anchor", "start")
            .style("font-size", textSize)
          // ----------------------

          let range = this.paceFilter(this.low, this.high, data)

          // For test on change the length of trace
          data[i]['states'].splice(data[i]['states'].length/slicePartition, data[i]['states'].length)
          data[i]['eventtypes'].splice(data[i]['eventtypes'].length/slicePartition, data[i]['eventtypes'].length)
          //----------------------------------------
          if (this.config.svgid_set.length == 0){
            Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, [data[i]], DataService.content.validSetCenter, this.config, false)
          }else{
            Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, [data[i]], DataService.content.validSetCenter, this.config, false)
          }
          orderNum = orderNum + 1
        }

        // For test on change the length of trace---------------------------------------------------------
        if (parseInt(data[i]['score'].length > 0 && data[i]['score'][data[i]['score'].length - 1]) < 100) {
          let currentScore = parseInt(data[i]['score'][data[i]['score'].length - 1])
          // Keep score's type as Number and keep the latest score
          data[i]['score'][0] = parseInt(data[i]['score'][data[i]['score'].length - 1])
          let currentUserid = data[i]['userid'].slice(11);
          let currentActNum = parseInt(data[i]['states'].length/3);
            
          let localsvg = mainSVG.append('g')
            .attr("id", "user" + i)
            .attr("transform", "translate(" + mapGap * secondOrderNum + ", 140)")

          d3.select('#bottomview_svg').append('text')
            .attr("x", textGap + mapGap * secondOrderNum)
            .attr("y", 60 + 140)
            .text("User ID:" + currentUserid)
            .attr("class", "textselected")
            .style("text-anchor", "start")
            .style("font-size", textSize)
          d3.select('#bottomview_svg').append('text')
            .attr("x", textGap + mapGap * secondOrderNum)
            .attr("y", 80 + 140)
            .text("Score:" + currentScore)
            .attr("class", "textselected")
            .style("text-anchor", "start")
            .style("font-size", textSize)
          d3.select('#bottomview_svg').append('text')
            .attr("x", textGap + mapGap * secondOrderNum)
            .attr("y", 100 + 140)
            .text("ActNum:" + currentActNum)
            .attr("class", "textselected")
            .style("text-anchor", "start")
            .style("font-size", textSize)
          d3.select('#bottomview_svg')
            .append("line")
            .attr("x1", mapGap * (secondOrderNum + 1))
            .attr("y1", 0 + 140)
            .attr("x2", mapGap * (secondOrderNum + 1))
            .attr("y2", 140 + 140)
            .attr("stroke", "grey")
            .attr("stroke-width", "2px")
            .attr('opacity', 0.5);

          let range = this.paceFilter(this.low, this.high, data)

          data[i]['states'].splice(data[i]['states'].length/slicePartition, data[i]['states'].length)
          data[i]['eventtypes'].splice(data[i]['eventtypes'].length/slicePartition, data[i]['eventtypes'].length)
 
          if (this.config.svgid_set.length == 0){
            Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, [data[i]], DataService.content.validSetCenter, this.config, false)
          }else{
            Object.getPrototypeOf(DrawService).drawTraceOverview(localsvg, range, [data[i]], DataService.content.validSetCenter, this.config, false)
          }
          secondOrderNum = secondOrderNum + 1
        //-------------------------------------------------------------------------------------------------
        }
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