<template>
  <div>
      <svg id="dataanalytics"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3'
import DrawService from "../services/draw-service"
import DataService from '../services/data-service'
import { eventBus } from '../eventBus';
export default {
  name: 'DataAnalyticsView',
  data () {
    return {
      svgid:"",
      showdataanalyticsview: true,
      config: {
        width: 300,
        height: 480,
        problemid: "20x746187641c59c168",
        userid: '0474000000008137',
      }
    }
  },
  mounted () {
    eventBus.$on("changeProb", arr => {
      this.config.problemid = arr[0]
      Object.getPrototypeOf(DataService).getUserSequenceByProblem.call(this, "renderTransition", this.config)
    })
  },
  methods: {
    renderTransition (data) {
      let localsvg = d3.select('#dataanalytics')
          .attr('class', 'DA_SVG')
          .attr("width", this.config.width)
          .attr('height', this.config.height)
      Object.getPrototypeOf(DrawService).drawchart(data, localsvg, this.config)
    }
}
}
</script>