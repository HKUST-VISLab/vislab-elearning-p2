<template>
    <div class="modal-bg" id= "modal-bg" v-show="slotShow" style="height:100%; width: 100%; background-color: rgba(0, 0, 0, 0.5);">
        <div class="modal-container" id= "modal-container" style="height:700px; width: 1080px; background-color: #f2eee5; margin-top: 10%; margin-left:10%; border-radius:10px;">
            <div class="modal-header" id= "modal-title" style="background-color:#855F5D; border-radius:10px;">
            </div>
            <div class="modal-main" style = "height: 640px;overflow-y:scroll; overflow-x: scroll;">
            </div>
            <div class="modal-footer" style="margin:auto; height: 30px; background-color:(242,238,229, 0.5)">
                <button @click="hideModal" style="width: 80px; height: 25px; margin-left: 500px">关闭窗口</button>
            </div>
        </div>
    </div>
</template>

<script>
import * as d3 from 'd3'
import { eventBus } from '../eventBus';
import DataService from '../services/data-service';
import DrawService from '../services/draw-service'
export default {
    name: 'ModalSlot',
    data() {
        return {
            svgid:"",
            clusterList:[1, 2, 3],
            showbottomview: false,
            low: 10,
            high: 500,  
            config: {
                disableZoom: true,
                scalesize: 6,
                problemid: "20x746187641c59c168",
                userid: '0474000000008137',
                svgid_set: [],
                cellRadius: 4,
                imagePath: 'image/20x746187641c59c168.jpg',
                maxRadius: 30,
                minRadius: 10,
            },
        }
    },
    props: {
        slotShow: {
            type: Boolean,
            default: false
        },
    },
    mounted() {
        eventBus.$on("changeProb", arr => {
            this.svgid = "id" + parseInt(Math.random() * 100000)
            this.config.svgid_set.push(this.svgid)
            this.config.cellRadius = arr[1]
            this.config.problemid = arr[0]
            this.config.imagePath = 'image/' + this.config.problemid + '.jpg'
        })
        eventBus.$on("view_change", chosenview => {
            if(chosenview == 'transitionview') {
                Object.getPrototypeOf(DataService).getClusterResultByProblem.call(this, "slotContain", this.config)
            }
        })
    
    },
    methods: {
        slotContain(clusterRes) {
            console.log(clusterRes)
            d3.select('.modal-header').selectAll('*').remove();
            d3.select('.modal-main').selectAll('*').remove();
            let slotWindowWidth = document.getElementById("modal-container").style.width,
                slotWindowHeight = document.getElementById("modal-container").style.height,
                headerHeight = 30,
                footerHeight = 30;
            let headerSVG = d3.select('.modal-header').append('svg')
                .attr('width', slotWindowWidth)
                .attr('height', headerHeight)
                .style('border-radius', 10),
                containSVG = d3.select('.modal-main').append('svg')
                .attr('width', slotWindowWidth)
                .attr('height', Number(String(slotWindowHeight).split('p')[0]) - headerHeight - footerHeight - 8),
                footerSVG = d3.select('.modal-footer').append('svg')
                .attr('width', slotWindowWidth)
                .attr('height', footerHeight);
            headerSVG.append('text')
                .text('Cluster')
                .attr('fill', 'white')
                .attr('font-size', 25)
                .attr('text-anchor', 'middle')
                .attr('transform', 'translate(' + (Number(String(slotWindowWidth).split('p')[0]) * 0.5) + "," + (headerHeight - 5) +")")

            // Draw cluster result
            Object.getPrototypeOf(DrawService).drawClusterView(containSVG, clusterRes[1], clusterRes[0], DataService.content.validSetCenter, 1, this.config)
            
        },
        hideModal() {
            this.$emit('hideModal')
        },
    }
}
</script>