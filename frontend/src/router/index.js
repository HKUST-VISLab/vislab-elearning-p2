import Vue from 'vue'
import Router from 'vue-router'
// import ROIview from '@/components/ROIview'
import SidePanel from '@/components/sidePanel'

Vue.use(Router)

export default new Router({
    routes: [{
        path: '/',
        name: 'SidePanel',
        component: SidePanel,
    }]
})