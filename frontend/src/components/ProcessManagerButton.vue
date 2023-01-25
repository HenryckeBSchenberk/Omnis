<template>
  <div>
    <div class="text-center">
      <v-dialog v-model="dialogStart" width="600">
        <v-card :loading="$apollo.loading">
          <v-card-title class="text-h4 lighten-2 d-flex flex-nowrap">
            <v-btn v-if="step2" icon @click="(step1 = true), (step2 = false)"
              ><v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <div class="ml-2">
              {{
                $t('dialogs.selectProcess')
              }}
            </div>
          </v-card-title>
          <v-card-text max-height="50vh">
            <v-card
              link
              v-for="(item, index) in get_process_list" :v-on="setObjectID(item.object._id)"
              :key="index"
              class="mx-auto"
              @click="selectedProcess(item._id)"
            >
            <v-tooltip top >
              <template v-slot:activator="{ on }">
                <!-- <div class="viewer"></div> -->
                <div class="pl-4 pr-4 my-4" v-on='on'>
                  <v-card-text class="text-center text-subtitle text-capitalize font-weight-bold">{{ item.name}}</v-card-text>
                  <!-- <div class="text-subtitle-2">{{ item.description }}</div> -->
                </div>
              </template>
              <span>{{ item._id }}</span>
            </v-tooltip>
            </v-card>
          </v-card-text>
        </v-card>
      </v-dialog>
    </div>
    <v-btn
      rounded
      x-large
      color="warning"
      dark
      class="mr-3"
      @click="commandSelector()"
    >
      <span
        ><v-icon left>mdi-{{ status[actualStatus].icon }}</v-icon></span
      >
      {{ status[actualStatus].text }}
    </v-btn>
    <v-btn
      v-if="actualStatus == 'paused'"
      rounded
      x-large
      color="error"
      dark
      @click="sendCommand(stop.command)"
    >
      <span
        ><v-icon left>mdi-{{ stop.icon }}</v-icon></span
      >
      {{ stop.text }}
    </v-btn>
  </div>
</template>

<script>
import gql from 'graphql-tag';
import MatrixViewer from './node/nodes/matrix/MatrixViewer.vue';
import { mapActions } from 'vuex';

const START = gql`
  mutation START {
    start_process
  }
`;

const PAUSE = gql`
  mutation PAUSE {
    pause_process
  }
`;

const RESUME = gql`
  mutation RESUME {
    resume_process
  }
`;

const STOP = gql`
  mutation STOP {
    stop_process
  }
`;

const LIST_PROCESS = gql`
  query LIST_PROCESS {
    get_process_list {
      _id
      name
      object {
        _id
        content
        }
      }
    }
`;

const LIST_OBJECT = gql`
  query LIST_OBJECT {
    get_object_list {
      _id
    }
  }
`;

const SELECT_PROCESS = gql`
  mutation SELECT_PROCESS($_id: ID!) {
    select_process(_id: $_id)
    start_process
  }
`;

export default {
  components: { MatrixViewer },
  name: 'ProcessManagerButton',
  data() {
    return {
      localData: null,
      actualStatus: 'stopped',
      dialogStart: false,
      filteredList: [],
      step1: false,
      step2: false,
      step3: false,
      process_object_link: [],
      get_matrix_list: [],
      process: [],
    };
  },

  created() {
    this.connectToWebsocket();
  },

  apollo: {
    get_process_list: LIST_PROCESS
    // get_object_list: LIST_OBJECT,
  },

  computed: {
    status() {
      return {
        running: {
          icon: 'pause',
          text: this.$t('buttons.pause'),
          command: PAUSE,
        },
        stopped: {
          icon: 'play',
          text: this.$t('buttons.start'),
          command: START,
        },
        paused: {
          icon: 'play',
          text: this.$t('buttons.resume'),
          command: RESUME,
        },
      };
    },
    stop() {
      return {
        icon: 'stop',
        text: this.$t('buttons.stop'),
        command: STOP,
      };
    },
  },

  methods: {
    ...mapActions('object', ['setObjectID']),
    async selectedProcess(_id) {
      console.log('select', _id);
      await this.$apollo
        .mutate({
          mutation: SELECT_PROCESS,
          variables: {
            _id,
          },
        })
        .then(() => {
          // Result
          this.dialogStart = false;
        })
        .catch((error) => {
          // Error
          this.isLoading = false;
          this.$alertFeedback(
            this.$t('alerts.failToRunProcess'),
            'error',
            error
          );
          // We restore the initial user input
        });
    },

    selectedObject(object) {
      // Separa todos os processos que tem esse objeto
      this.process_object_link = this.get_process_list.filter(
        (element) =>
          element.object.filter((item) => item.name === object.name).length
      );
      this.step1 = false;
      this.get_matrix_list = [];

      // Separa as matrizes desses objetos, em uma lista a parte
      this.process_object_link.forEach((element) => {
        element.object.forEach((object) => {
          object.matrix.forEach((matrix) => {
            this.get_matrix_list.push(matrix);
          });
        });
      });

      // Remove as duplicatas (quando mais de um objeto usa a mesma matriz)
      this.get_matrix_list = this.get_matrix_list.filter(
        (thing, index, self) =>
          self.findIndex((t) => t._id === thing._id) === index
      );
    },

    selectedMatrix(matrix) {
      // Filtra dentro dos processos selecionados anteriormente, somente aqueles que possuem um objeto,
      // que possua a matrix selecionada.
      this.process = this.process_object_link.filter(
        (element) =>
          element.object.filter(
            (object) =>
              object.matrix.filter((matrixx) => matrixx.name == matrix.name)
                .length
          ).length
      );

      this.step3 = true;
    },

    commandSelector() {
      const status = this.status[this.actualStatus].command;
      if (status === START) {
        this.dialogStart = true;
        this.step1 = true;
      } else {
        this.sendCommand(status);
      }
    },

    async sendCommand(command) {
      await this.$apollo
        .mutate({
          mutation: command,
        })

        .then(() => {})

        .catch((error) => {
          this.$alertFeedback('alerts.updateMatrixSuccess', 'error', error);
          // We restore the initial user input
        });
    },

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
  },
};
</script>

<style>
</style>
