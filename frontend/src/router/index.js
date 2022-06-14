import Vue from 'vue';
import Router from 'vue-router';

import Dashboard from '@/views/Dashboard.vue';
import Default from '@/views/settings/Default.vue';
import Devices from '@/views/settings/Devices.vue';
import Home from '@/views/Home.vue';
import IntroLogo from '@/views/IntroLogo.vue';
import Network from '@/views/settings/Network.vue';
import NodeConfig from '@/views/NodeConfig.vue';
import NodeEditor from '@/components/node/NodeEditor.vue';
import NodeWorkspace from '@/views/NodeWorkspace.vue';
import Progress from '@/views/Progress.vue';
import Scan from '@/views/Scan.vue';
import Settings from '@/views/Settings.vue';
import Success from '@/views/Success.vue';
import System from '@/views/settings/System.vue';
import Support from '@/views/settings/Support.vue';
import Process from '@/views/settings/Process.vue';
import MatrixDirectionSelector from '@/components/node/config/matrix/MatrixDirectionSelector.vue';
import Users from '@/views/settings/Users.vue';

Vue.use(Router);

const routes = [
  {
    name: 'home',
    path: '/home',
    component: Home,
  },
  {
    name: 'settings',
    path: '/config',
    component: Settings,
    meta: {
      breadCrumb: 'Configurações',
    },
    children: [
      {
        component: Default,
        name: 'default',
        path: '',
      },
      {
        name: 'network',
        component: Network,
        path: 'network',
        meta: {
          breadCrumb: 'Rede & Internet',
        },
      },
      {
        name: 'system',
        component: System,
        path: 'system',
        meta: {
          breadCrumb: 'Sistema',
        },
      },
      {
        name: 'devices',
        component: Devices,
        path: 'devices',
        meta: {
          breadCrumb: 'Dispositivos',
        },
      },
      {
        name: 'users',
        component: Users,
        path: 'users',
        meta: {
          breadCrumb: 'Usuários',
        },
      },
      {
        name: 'support',
        component: Support,
        path: 'support',
        meta: {
          breadCrumb: 'Suporte',
        },
      },
      {
        name: 'process',
        component: Process,
        path: ':process',
        meta: {
          breadCrumb: 'Processo',
        },
        children: [
          {
            name: 'matrix',
            component: MatrixDirectionSelector,
            path: ':matrix',
            meta: { breadCrumb: 'Matriz' },
          },
        ],
      },
      // {
      //   name: 'matrix',
      //   component: MatrixDirectionSelector,
      //   path: ':matrix',
      //   meta: {
      //     breadCrumb: 'Matriz', //crumb
      //   },
      // },
    ],
  },
  {
    name: 'intro-logo',
    path: '/',
    component: IntroLogo,
  },
  {
    name: 'scan',
    path: '/scan',
    component: Scan,
  },
  {
    name: 'progress',
    path: '/progress',
    component: Progress,
  },
  {
    name: 'success',
    path: '/success',
    component: Success,
  },
  {
    name: 'dashboard',
    path: '/dashboard',
    component: Dashboard,
  },
  {
    name: 'node',
    path: '/node',
    component: NodeWorkspace,
  },
  {
    name: 'nodeEditor',
    path: '/node-editor',
    component: NodeEditor,
  },
  {
    name: 'nodeConfig',
    path: '/node-config',
    component: NodeConfig,
  },
  // {
  //   path: '*',
  //   redirect: '/',
  // },
];

const router = new Router({ ...{ mode: 'history' }, routes });

export default router;
