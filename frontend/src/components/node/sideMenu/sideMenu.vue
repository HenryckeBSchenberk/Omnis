<template>
  <div class="container">
    <v-btn
      dark
      :style="tabButton"
      class="tab-button"
      :class="drawer ? 'active' : ''"
      color="#4e4e4e"
      @click.stop="drawer = !drawer"
      >movimentação</v-btn
    >
    <v-navigation-drawer
      :style="navigationDrawer"
      v-model="drawer"
      width="400px"
      right
      dark
      app
      :absolute="drawer"
      :permanent="drawer"
    >
      <move :actualStatus="actualStatus"></move>
    </v-navigation-drawer>
  </div>
</template>

<script>
import Move from '@/components/node/sideMenu/move/Move.vue';

export default {
  components: {
    Move,
  },

  props: {
    paddingTop: String,
  },

  data: () => ({
    drawer: false,
    group: null,
    actualStatus: 'stopped',
  }),

  created() {
    this.connectToWebsocket();
  },

  computed: {
    navigationDrawer() {
      return {
        'padding-top': this.paddingTop,
      };
    },
    tabButton() {
      return {
        'margin-top': this.paddingTop,
      };
    },
  },

  watch: {
    group() {
      this.drawer = false;
    },
  
  },

  methods:{
    connectToWebsocket() {
      console.log(this.$t('alerts.wsConnecting'));
      this.WebSocket = new WebSocket(
        `ws://${process.env.VUE_APP_URL_API_IP}:${process.env.VUE_APP_URL_API_PORT}/process`
      );

      this.WebSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.actualStatus = data.status.toLowerCase();
      };

      this.WebSocket.onopen = (event) => {
        console.log(event);
        console.log(this.$t('alerts.wsConnectSuccess'));
      };

      this.WebSocket.onclose = (event) => {
        console.log(
          'Socket is closed. Reconnect will be attempted in 1 second.',
          event.reason
        );
        setTimeout(
          () => this.connectToWebsocket(),
          Math.floor(Math.random() * 2500)
        );
      };
    },
  }
};
</script>

<style lang="scss" scoped>
.container {
  padding: 0;
  .tab-button {
    transform: rotate(-90deg);
    transform-origin: 92%;
    position: absolute;
    top: 20px;
    z-index: 1;
    right: 3px;
  }
  .active {
    transform: rotate(-90deg) translateY(-398px);
  }
}
</style>