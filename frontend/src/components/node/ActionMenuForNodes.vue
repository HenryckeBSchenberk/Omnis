/* eslint-disable no-underscore-dangle */
<template>
  <div class="actions-container">
    <div  class="menuList" v-on:keyup.ctrl.s="save">
      <v-speed-dial
        v-model="fab"
        direction="top"
        transition="slide-x-transition"
        class="d-flex flex-end speed-dial"
      >
        <template v-slot:activator>
          <v-btn color="primary" fab dark>
            <v-icon v-if="fab"> mdi-close </v-icon>
            <v-icon dark v-else> mdi-dots-vertical </v-icon>
          </v-btn>
        </template>
        <v-btn
          color="primary"
          class="option"
          dark
          v-for="(item, index) in items"
          :key="index"
          @click="findFunction(item.method)"
        >
          <v-icon left dark>{{ item.icon }} </v-icon>{{ item.title }}
        </v-btn>
        <!-- <v-btn color="primary" class="" dark @change="upload"> -->
        <input
          id="fileUpload"
          type="file"
          hidden
          @change="upload"
          accept=".oms,"
        />
        <v-btn v-show="false" color="primary" class="option" dark @click="chooseFiles()">
          <v-icon left dark>mdi-upload</v-icon>Upload
        </v-btn>
        <v-btn color="primary" class="option" dark @click="folderDialog = true">
          <v-icon left dark>mdi-folder</v-icon>Arquivos
        </v-btn>
        <v-btn color="primary" class="option" dark @click="serialDialog = true">
          <v-icon left dark>mdi-console</v-icon>Serial
        </v-btn>
      </v-speed-dial>

      <v-btn dark fab class="button" color="primary" @click="commandSelector()">
        <v-icon>mdi-{{ status[actualStatus].icon }}</v-icon>
      </v-btn>
      <v-btn
        v-if="actualStatus != 'stopped'"
        fab
        class="button"
        color="primary"
        dark
        @click="sendCommand(stop.command)"
      >
        <v-icon>mdi-{{ stop.icon }}</v-icon>
      </v-btn>
    </div>
    <v-progress-linear
      v-if="isLoading"
      fixed
      indeterminate
      color="cyan"
      bottom
    ></v-progress-linear>
    <v-dialog
      dark
      v-model="folderDialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
      ><v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="folderDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Arquivos</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>
        <div class="pa-12" v-if="folderDialog">
          <sketch-explorer
            @close-dialog="folderDialog = false"
          ></sketch-explorer>
        </div>
      </v-card>
    </v-dialog>
    <v-dialog
      dark
      v-model="serialDialog"
      transition="dialog-bottom-transition"
      max-width="750px"
      ><v-card>
        <div class="pa-5" v-if="serialDialog">
          <serial-monitor></serial-monitor>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex';
import gql from 'graphql-tag';

import { UPDATE_SKETCH, CREATE_SKETCH } from '@/graphql';

import SketchExplorer from '@/components/node/SketchExplorer.vue';
import SerialMonitor from '@/components/SerialMonitor.vue';

const START = gql`
  mutation START($id: ID!, $object_id: ID) {
    start_process(_id: $id, object_id:$object_id)
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

export default {
  name: 'ActionMenuForNodes',
  components: {
    SketchExplorer,
    SerialMonitor,
  },

  data() {
    return {
      actualStatus: 'stopped',
      folderDialog: false,
      serialDialog: false,
      fab: false,
      fling: false,
      tabs: null,
      files: null,
      result_: 'Teste',
      transition: 'slide-x-transition',
      loadedId: null,
      items: [
        {
          title: 'Salvar',
          icon: 'mdi-content-save',
          method: 'save',
        },
        { title: 'Download', icon: 'mdi-file-download', method: 'download' },
        // { title: 'Upload', icon: 'mdi-file-upload', method: 'upload' },
      ],
      isLoading: false,
    };
  },

  created() {
    this.connectToWebsocket();
  },

  computed: {
    ...mapState('node', {
      selectedTabIndex: (state) => state.selectedTabIndex,
      tabList: (state) => state.tabList,
      selectedTab: (state) => state.selectedTab,
      editor: (state) => state.editor,
    }),
    ...mapState('object', ['object_id']),

    ...mapGetters('node', [
      'selectedTabName',
      'selectedTabObject', // -> this.getTabName
    ]),

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
    ...mapActions('node', ['play', 'setSaved']),

    connectToWebsocket() {
      console.log(this.$t('alerts.wsConnecting'));
      this.WebSocket = new WebSocket(`ws://${process.env.VUE_APP_URL_API_IP}:${process.env.VUE_APP_URL_API_PORT}/process`);

      this.WebSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data)
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

    commandSelector() {
      const status = this.status[this.actualStatus].command;
      this.sendCommand(status);
    },

    async sendCommand(command) {
      if (command === START) await this.save();
      await this.$apollo
        .mutate({
          mutation: command,
          variables: {
            // eslint-disable-next-line no-underscore-dangle
            id: this.selectedTab._id,
            object_id: this.object_id,
          },
        })

        .then(() => {})

        .catch((error) => {
          this.$alertFeedback(
            this.$t('alerts.runningProcessFail'),
            'error',
            error.message
          );
          // We restore the initial user input
        });
    },

    chooseFiles() {
      document.getElementById('fileUpload').click();
      // console.log(this.$alertFeedback);
      // this.$alertFeedback('Uploading...', 'info');
      // this.$alertFeedback('George', 'info');
    },

    findFunction(name) {
      this[name]();
    },

    async save() {
      const tabToSave = this.selectedTab;
      this.isLoading = true;

      if (tabToSave.created && !tabToSave.saved) {
        console.log('create');
        console.log('tab to create', tabToSave);

        await this.$apollo
          .mutate({
            mutation: CREATE_SKETCH,
            variables: {
              // eslint-disable-next-line no-underscore-dangle
              _id: tabToSave._id,
              parent_id: tabToSave.parent_id,
              name: tabToSave.label,
              description: `${tabToSave.name} descrição`,
              version: tabToSave.version,
              // key: tabToSave.key,
              saved: tabToSave.saved,
              duplicated: tabToSave.duplicated,
              content: this.editor.save(),
            },
          })
          .then(() => {
            // Result
            this.$alertFeedback('alerts.saveSuccess', 'success');
            this.isLoading = false;
            console.log(this.selectedTabIndex);
            this.setSaved({ index: this.selectedTabIndex, value: true });
          })
          .catch((error) => {
            // Error
            this.isLoading = false;
            this.$alertFeedback('alerts.saveFail', 'error', error);

            // We restore the initial user input
          });
      } else {
        console.log('update');
        console.log('tab to update', tabToSave);

        await this.$apollo
          .mutate({
            mutation: UPDATE_SKETCH,
            variables: {
              // eslint-disable-next-line no-underscore-dangle
              _id: tabToSave._id,
              parent_id: tabToSave.parent_id,
              name: tabToSave.label,
              description: `${tabToSave.name} descrição`,
              version: tabToSave.version,
              // key: tabToSave.key,
              saved: tabToSave.saved,
              duplicated: tabToSave.duplicated,
              content: this.editor.save(),
            },
          })
          .then((data) => {
            // Result
            console.log(data);
            this.$alertFeedback('alerts.saveSuccess', 'success');
            this.isLoading = false;
            // this.setSaved({ index: this.selectedTabIndex, value: true });
          })
          .catch((error) => {
            // Error
            this.isLoading = false;
            this.$alertFeedback('alerts.saveFail', 'error', error);

            // We restore the initial user input
          });
      }
    },

    download() {
      function download(content, fileName, contentType) {
        const a = document.createElement('a');
        const file = new Blob([content], { type: contentType });
        a.href = URL.createObjectURL(file);
        a.download = fileName;
        a.click();
      }
      const fileName = this.tabList[this.selectedTabIndex].name;
      download(
        JSON.stringify(this.tabList[this.selectedTabIndex]),
        `${fileName}.oms`,
        'text/oms'
      );
    },

    out() {
      console.log(this);
    },

    async upload({ target }) {
      this.fab = false;
      console.log(target.files[0].name.split('.').pop());

      if (
        target.files[0].name.split('.').pop() !== 'oms' &&
        target.files[0].name.split('.').pop() !== 'json'
      ) {
        this.$alertFeedback('alerts.invalidFile', 'error');

        return;
      }

      // console.log(target.files[0].name.split('.').pop());
      const { files } = target;
      const fr = new FileReader();
      console.log(files);
      if (files.length <= 0) {
        return;
      }

      let json;

      async function loadFile(callback) {
        console.log(callback);
        fr.onload = async (e) => {
          json = JSON.parse(e.target.result);
          await callback();
        };
      }

      // Use time out to wait for the file to be read
      fr.readAsText(files[0]);
      this.isLoading = true;
      loadFile(async () => {
        console.log(json);
        this.editor.load(json);
        this.isLoading = false;
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.actions-container {
  position: absolute;
}
.menuList {
  display: flex;
  flex-direction: row;
  align-items: center;

  .button {
    margin-left: 0.5rem;
  }
  .option{
    width: 9rem;
    justify-content: left;
  }
}

::v-deep .v-speed-dial--direction-top .v-speed-dial__list {
  align-items: baseline;
}
</style>
