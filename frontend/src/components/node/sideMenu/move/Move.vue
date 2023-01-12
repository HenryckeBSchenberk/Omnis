<template>
  <div class="p-2 pl-4 d-flex flex-column">
    <v-fade-transition>
      <v-overlay 
        color="blue-grey darken-4"
        absolute
        opacity="0.85"
        :value="actualStatus !== 'stopped'">
    
        <div 
          class="align-center d-flex flex-column justify-center text-center text-h6 text-uppercase "
        > 
        <v-icon large> mdi-lock </v-icon>
        Em processo 
      </div>
    </v-overlay>
  </v-fade-transition>
  <div v-if="$access('jogButtons')">
      <jog-buttons
        :axisDistances="axisDistances"
        @send="sendMessage"
      ></jog-buttons>
      <scale-movement @send="sendMessage"></scale-movement>
    </div>
    <output-devices
      v-if="$access('outputDevices')"
      @send="sendMessage"
    ></output-devices>
    <macros v-if="$access('macros')" @send="sendMessage"></macros>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import OutputDevices from './OutputDevices.vue';
import JogButtons from './JogButtons.vue';
import ScaleMovement from './ScaleMovement.vue';
import Macros from './Macros.vue';

export default {
  components: {
    JogButtons,
    ScaleMovement,
    OutputDevices,
    Macros,
  },
  props:{
    actualStatus: String
  },
  data() {
    return {
      axisDistances: {},
    };
  },

  created() {
    this.connectToWebsocket();
  },

  methods: {
    ...mapActions('node', ['updateControls']),

    sendMessage(data) {
      console.log('sendMessage', data);
      if (this.WebSocket.readyState === 1) {
        console.log('Ws sended:', data);
        this.WebSocket.send(JSON.stringify(data));
      }
    },

    connectToWebsocket() {
      console.log(this.$t('alerts.wsConnecting'));
      this.WebSocket = new WebSocket(
        `ws://${process.env.VUE_APP_URL_API_IP}:${process.env.VUE_APP_URL_API_PORT}/controls/6244b0ad3a8338aceae46cf1`,
      );

      this.WebSocket.onmessage = (event) => {
        // console.log(event);
        this.axisDistances = JSON.parse(event.data);
        this.updateControls(this.axisDistances);
      };

      this.WebSocket.onopen = (event) => {
        console.log(event);
        console.log(this.$t('alerts.wsConnectSuccess'));
      };

      this.WebSocket.onclose = (event) => {
        console.log(
          'Socket is closed. Reconnect will be attempted in 1 second.',
          event.reason,
        );
        setTimeout(
          () => this.connectToWebsocket(),
          Math.floor(Math.random() * 2500),
        );
      };
    },
  },
};
</script>
