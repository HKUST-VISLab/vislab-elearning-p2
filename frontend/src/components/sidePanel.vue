<template>
  <div class="appcontent">
    <div class="slotPart">
        <ModalSlot :slotShow="slotShow" @hideModal="hideModal" style="position: absolute" />
    </div>
    <div class="leftPart">
      <div class="overviewtitle">Overview</div>
      <div class="overviewcontainer">
        <ROIview :cellRadius="cellRadius" :cellCoef="cellCoef" :upperThresh="upperThresh" :lowerThresh="lowerThresh" :problemid="problemid"/>
        <HeatMapview :heatRadius="heatRadius" :heatCoef="heatCoef" :freqThresh="freqThresh" :problemid="problemid"/>
        <Transitionview :cellRadius="cellRadius" :problemid="problemid" :maxRadius="maxRadius" :minRadius="minRadius"/>
      </div>
      <div class="transitiontitle">Transition Map</div>
      <div class="transitioncontainer" >
        <BottomView @showSlot="showSlot"/>
      </div>
    </div>
    <div class="rightPart">
      <div id = "id_panel" class="range-slider slider-menu">
        <div class="paneltitle">
          Control Panel
        </div>
        <div class="panelcontainer">
          <select @change="viewChange" v-model="viewvalue" style="height:40px;width: 90%;margin-left: 5%;margin-top: 2px;">
                  <option value="roiview">ROI View</option>
                  <option value="heatmapview">HeatMap View</option>
                  <option value="transitionview">Transiton View</option>
          </select>
          <div v-if="viewvalue==='roiview'" class="panelcontent">
              <span><input @change="valueChange" v-model.number="cellRadius"  class="input-range" type="range" min="1" max="20">Cell Radius</span>
              <span><input @change="valueChange" v-model.number="cellCoef"    class="input-range" type="range" min="1" max="40">Cell Coefficient</span>
              <span><input @change="valueChange" v-model.number="upperThresh" class="input-range" type="range" min="1" max="500">Frequency Upper Threshold</span>
              <span><input @change="valueChange" v-model.number="lowerThresh" class="input-range" type="range" min="1" max="400">Frequency Lower Threshold</span>
              <span>
                  <input type="radio" @change="changeMode" value="false" v-model="mode">Upper Mode
                  <input type="radio" @change="changeMode" value="true" v-model="mode">Lower Mode
              </span>
          </div>
          <div v-if="viewvalue==='heatmapview'" class="panelcontent">
              <span><input @change="valueChange" v-model.number="heatRadius" class="input-range" type="range" min="0" max="20">Hotspot Radius</span>
              <span><input @change="valueChange" v-model.number="heatCoef" class="input-range" type="range" min="0" max="40">Smoothing Coefficient</span>
              <span><input @change="valueChange" v-model.number="freqThresh" class="input-range" type="range" min="1" max="100">Frequency Threshold</span>
          </div>
          <div v-if="viewvalue==='transitionview'" class="panelcontent">
              <span><input @change="valueChange" v-model.number="maxRadius" class="input-range" type="range" min="20" max="50">Max Radius (Pie)</span>
              <span><input @change="valueChange" v-model.number="minRadius" class="input-range" type="range" min="10" max="20">Min Radius (Pie)</span>
          </div>
        </div>
      </div>
      <div id = "id_statistic" style="margin-left:10px;margin-top:5px">
        <div class="statistictitle">
          Data Analytics
        </div>
        <div class="statiscontainer">
          <DataAnalyticsView/>
        </div>
      </div>
    </div>
    <div>
      <div class="plist">
        <img @click="changeProblem($event)" :name="item" :class="item==problemid?'pimg-selected':'pimg'" :src="'static/img/'+item+'.jpg'" v-for="item in problemlist" v-bind:key="item">
      </div>
    </div>
  </div>
</template>

<script>
import ROIview from './ROIview'
import DataService from '../services/data-service'
import HeatMapview from './HeatMap'
import Transitionview from './Transition'
import BottomView from './BottomView'
import DataAnalyticsView from './DataAnalytics'
import ModalSlot from './Clusterslot'
import { eventBus } from "../eventBus.js"

export default {
  name: 'SidePanel',
  components: {
    ROIview,
    HeatMapview,
    Transitionview,
    BottomView,
    DataAnalyticsView,
    ModalSlot,
  },
  data () {
    return {
      problemlist: ["2841x00378c88165f5e16","3390x89c89efbd95796b2","3193xfa9eefc38d8ea289","3192x96c2dcdc94eac57b", "3345x563ac713a3b6df9f","93x86d2ce608bf1ee27", "20x746187641c59c168","21x92b56cf7078123e4", "22x9b87945d0701947f","2350x67dbe3cf12d34feb","3194xb3570a05e04eaa46","2344x8773a6898a1f33cf","2352x2c01d405736101be","2343xccc49157c296ccd8","392xbf8da0c8c5262b4b","174x4dc558a71c4020b7","583x8935c42f1e095c80","2288x7f5a6f65dd75801d","3331xde2f4ef708d49596","17x20d0226967291fe3","3260x04b8302ee2f3e356","3214xd1ecb03eaf4ed53a","2933x1aec2bd4ca7bf1ca","545x81d6ae36725e90e1","2957x081413147870fe2a","3560x3937fea475445c30","680xf0cb97b391c7b6b8","3333xbe2b90abda67f262","3332xfbbe2cb982db7c99","611xca233ae480904689"],
      viewvalue: "roiview",
      cellRadius: 4,
      cellCoef: 13,
      upperThresh: 209,
      lowerThresh: 200,
      heatRadius: 3,
      heatCoef: 4,
      freqThresh: 11,
      maxRadius: 30,
      minRadius: 10,
      mode: "false",
      problemid: "20x746187641c59c168",
      slotShow: false,
    }
  },
  mounted () {
    this.changeProblem()
  },
  methods: {
    initProblemConfig (cfg) {
      if(Object.keys(cfg).length > 0){
        this.cellRadius = parseInt(cfg.config.cellRadius)
        this.cellCoef = parseInt(cfg.config.cellCoef)
        this.upperThresh = parseInt(cfg.config.upperThresh * 1000)
        this.lowerThresh = parseInt(cfg.config.lowerThresh * 1000)
      }
      eventBus.$emit("changeProb", [this.problemid, this.cellRadius, this.cellCoef, this.upperThresh, this.lowerThresh])
      this.viewvalue = "roiview"
      eventBus.$emit("view_change", this.viewvalue)
      this.valueChange()
    },
    changeProblem (e) {
      if(e && e.target){
        this.problemid = e.target.name
      }
      let userProb = {
        userid: '0474000000008137',
        problemid: this.problemid
      }
      Object.getPrototypeOf(DataService).getImportantArea.call(this, 'initProblemConfig', userProb);
    },
    valueChange () {
      if (this.viewvalue === 'roiview') {
        eventBus.$emit("roi_valuechange", [this.problemid, this.cellRadius, this.cellCoef, this.upperThresh, this.lowerThresh])
      }
    },
    changeMode () {
      eventBus.$emit("mode_change", this.mode)
    },
    viewChange () {
      eventBus.$emit("view_change", this.viewvalue)
      this.valueChange()
    },
    hideModal() {
        // 取消弹窗回调
        this.slotShow = false
    },
    showSlot() {
        this.slotShow = true
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.slider-menu {
    margin-left: 10px;
    display: grid;
}

.range-slider .input-range {
    -webkit-appearance: none;
    width: 100%;
    height: 10px;
    border-radius: 5px;
    background: lightgray;
    outline: none;
}

.range-slider span {
    border-bottom: 1px solid #ccc!important;
    padding: 5px;
}

.range-slider .input-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background: #666;
    cursor: pointer;
    -webkit-transition: background .15s ease-in-out;
    transition: background .15s ease-in-out;
}

.range-slider .input-range::-webkit-slider-thumb:hover {
    background: #fff;
}

.range-slider .input-range:active::-webkit-slider-thumb {
    background: #fff;
}

.range-slider .input-range::-moz-range-thumb {
    width: 15px;
    height: 15px;
    border: 0;
    border-radius: 50%;
    background: #666;
    cursor: pointer;
    -webkit-transition: background .15s ease-in-out;
    transition: background .15s ease-in-out;
}

.range-slider .input-range::-moz-range-thumb:hover {
    background: #fff;
}

.range-slider .input-range:active::-moz-range-thumb {
    background: #fff;
}

.range-slider .range-value {
    display: inline-block;
    position: relative;
    width: 60px;
    color: #fff;
    font-size: 16px;
    font-weight: bold;
    line-height: 20px;
    text-align: center;
    border-radius: 3px;
    background: #3f3f3f;
    padding: 5px 10px;
    margin-left: 7px;
}

.range-slider .range-value:after {
    position: absolute;
    top: 8px;
    left: -7px;
    width: 0;
    height: 0;
    border-top: 7px solid transparent;
    border-right: 7px solid #3f3f3f;
    border-bottom: 7px solid transparent;
    content: '';
}

.appcontent {
    display: flex;
}

.leftPart {
    width: 968px;
    margin-left: 10px;
}

.overviewtitle {
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    background: rgba(133, 95, 93);
    width: 968px;
    height: 25px;
    font-size: 20px;
    color: white;
    text-align: center;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif
}

.overviewcontainer {
    border: 4px solid rgba(186, 146, 146) !important;
    height: 600px;
}

.rightPart {
    width: 308px;
}

.plist {
    padding-left: 5px;
    overflow-y: scroll;
    height: 820px;
    display: grid;
}

.pimg {
    width: 100px;
    padding-top: 5px;
    border: 1px solid rgba(186, 146, 146) !important;
}

.pimg-selected {
    width: 100px;
    padding-top: 5px;
    border: 2px solid rgba(133, 95, 93)!important;
}

.paneltitle {
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    background: rgba(133, 95, 93);
    width: 300px;
    height: 25px;
    font-size: 20px;
    color: white;
    text-align: center;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif
}

.panelcontainer {
    border: 4px solid rgba(186, 146, 146) !important;
    /* height: 600px; */
}

.panelcontent {
    width: 90%;
    display: grid;
    margin-left: 5%;
}

.transitiontitle {
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    background: rgba(133, 95, 93);
    margin-top: 5px;
    width: 968px;
    height: 25px;
    font-size: 20px;
    color: white;
    text-align: center;
    font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif
}

.transitioncontainer {
    border: 4px solid rgba(186, 146, 146) !important;
    /* height: 140px; */
    height: 280px;
}

.statistictitle {
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    background: rgba(133, 95, 93);
    width: 300px;
    height: 25px;
    font-size: 20px;
    color: white;
    text-align: center;
    font-family:'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif
}

.statiscontainer {
    border: 4px solid rgba(186, 146, 146) !important;
    height: 480px;
}

</style>
