<template>
  <div class='hello' v-show="showheatmap">
    <canvas id='id_heatmap' ref='id_heatmap' width='960' height='600'></canvas>
  </div>
</template>

<script>
import SidePanel from './sidePanel'
import DataService from '../services/data-service'
import * as empty from '../assets/lib/simpleheat'
import { eventBus } from "../eventBus.js"
export default {
  name: 'HeatMapview',
  data () {
    return {
      showheatmap: false,
      config: {
        problemid: "20x746187641c59c168",
        userid: '0474000000008137',
        heatRadius: this.heatRadius,
        heatCoef: this.heatCoef,
        freqThresh: this.freqThresh,
        heatmap: null,
      }
    }
  },
  props: {
    problemid: {
      required: true,
    },
    heatRadius: {
      type: Number,
      required: true,
    },
    heatCoef: {
      type: Number,
      required: true,
    },
    freqThresh: {
      type: Number,
      required: true,
    },
  },
  watch: {
    heatRadius(newValue, oldValue) {
        this.heatRadius = newValue
        this.config.heatRadius = this.heatRadius
        Object.getPrototypeOf(DataService).getSequence.call(this, 'drawHeatmap', this.config)
    },
    heatCoef(newValue, oldValue) {
        this.heatCoef = newValue
        this.config.heatCoef = this.heatCoef
        Object.getPrototypeOf(DataService).getSequence.call(this, 'drawHeatmap', this.config)
    },
    freqThresh(newValue, oldValue) {
        this.freqThresh = newValue
        this.config.freqThresh = this.freqThresh
        Object.getPrototypeOf(DataService).getSequence.call(this, 'drawHeatmap', this.config)
    },
  },  
  components: {

  },
  mounted () {
    eventBus.$on("view_change", chosenview => {
      this.config.problemid = this.problemid
      if(chosenview == 'heatmapview') {
        this.showheatmap = true
        Object.getPrototypeOf(DataService).getSequence.call(this, 'drawHeatmap', this.config)
      } else {
        this.showheatmap = false
      }
    })
  },
  methods: {
    drawHeatmap (rawdt) {
      let localdata = this._transferdata(rawdt)
      let heatEle = document.getElementById('id_heatmap')
      this.config.heatmap = Simpleheat(heatEle)
      this.config.heatmap.data(localdata)
      this.config.heatmap._max = this.config.freqThresh
      this.config.heatmap.radius(this.config.heatRadius, this.config.heatCoef)
      this.config.heatmap.draw()
    },
    _transferdata (dt) {
      let dtst = []
      for (let i = 0; i < dt.length; i++) {
        for (let t = 0; t < dt[i].length; t++) {
          if (dt[i][t] > 0) {
            dtst.push([i, t, dt[i][t]])
          }
        }
      }
      return dtst
    }
  }
}
</script>