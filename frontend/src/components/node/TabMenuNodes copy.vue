<template>
  <div class="content">
    <v-tabs align-with-title grow v-model="tab">
      <v-tab
        class="tab-item d-flex justify-space-between"
        @contextmenu="show"
        v-for="(item, index) in tabList"
        :key="index"
        @click="selectTab(index)"
        @click.middle="close(index)"
        @click.right="contextMenuSelectedTabIndex = index"
        v-model="tab"
      >
        <div>
          <v-icon
            small
            dark
            color="green accent-3"
            v-if="nameRunning == item.name"
          >
            mdi-play
          </v-icon>
          <div class="mb-n5" v-if="renamingIndex === index">
            <v-text-field
              :append-outer-icon="name ? 'mdi-check' : null"
              @click:append-outer="rename(index)"
              autofocus
              :value="tabList[index].name"
              v-model="name"
              @keyup.enter="name != '' ? rename(index) : tabList[index].name"
              single-line
              full-width
            ></v-text-field>
          </div>
          <span v-else>{{ +!item.saved ? item.name + '*' : item.name }}</span>
        </div>

        <!-- dropdown -->
        <v-menu
          transition="slide-x-transition"
          v-model="showMenu"
          bottom
          dark
          right
          :position-y="y"
          :position-x="x"
        >
          <v-list>
            <v-list-item
              class="list-item"
              v-for="(item, index) in items"
              :key="index"
              link
            >
              <v-list-item-title
                @click="item.function(contextMenuSelectedTabIndex)"
                ><v-icon small class="mr-5">mdi-{{ item.btnIcon }}</v-icon
                >{{ item.title }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

        <v-btn depressed icon small class="context-menu-btn">
          <v-icon small dark> mdi-dots-vertical </v-icon></v-btn
        >
        <v-btn
          v-if="tabList.length > 1"
          depressed
          icon
          @click="close(index)"
          small
        >
          <v-icon class="align-self-end" small dark> mdi-close </v-icon></v-btn
        >
      </v-tab>
      <v-btn class="add-tab" depressed icon @click="add()" small
        ><v-icon small dark> mdi-plus </v-icon></v-btn
      >
    </v-tabs>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import gql from 'graphql-tag';

const ObjectID = require('bson-objectid');

export default {
  name: 'TabMenuNodes',

  data() {
    return {
      tab: null,
      actualNode: null,
      length: 0,
      name: '',
      nameRunning: 'One',
      newTabCount: 1,
      lixo: null,
      tagAdded: {},
      contextMenuSelectedTabIndex: null,

      showMenu: false,
      x: 0,
      y: 0,
      items: [
        {
          title: 'Duplicar',
          btnIcon: 'content-duplicate',
          function: this.duplicate,
        },
        {
          title: 'Renomear',
          btnIcon: 'form-textbox',
          function: this.setRenamingIndex,
        },
      ],
      newTab: {
        name: '',
        description: 'Descrição',
        author: 'Autor',
        last_access: new Date().getTime(),
        _id: null,
        parent_id: null,
        version: 1,
        saved: false,
        duplicated: false,
        content: '',
      },
    };
  },

  computed: {
    ...mapState('node', {
      tabList: (state) => state.tabList,
      selectedTabId: (state) => state.selectedTabId,
      selectedTab: (state) => state.selectedTab,
      selectedTabIndex: (state) => state.selectedTabIndex,
      contentDefault: (state) => state.contentDefault,
      renamingIndex: (state) => state.renamingIndex,
    }),
  },

  watch: {
    selectedTabIndex(newValue) {
      console.log(`nova ${newValue} tab: ${this.tab}`);
      this.tab = newValue;
    },
  },

  methods: {
    ...mapActions('node', [
      'addTab',
      'removeTabById',
      'selectTabByIndex',
      'removeTabByIndex',
      'play',
      'updateSelectedTab',
      'duplicateTab',
      'setRenamingIndex',
      'setSketchName',
    ]),

    show(e) {
      e.preventDefault();
      this.showMenu = false;
      this.x = e.clientX;
      this.y = e.clientY;
      this.$nextTick(() => {
        this.showMenu = true;
      });
    },

    async apollo() {
      // console.time('apollo');
      const response = await this.$apollo.query({
        query: gql`
          query {
            getProcess {
              data {
                status
              }
            }
          }
        `,
      });
      // console.log(this.$apollo.store);
      this.lixo = response.data.getProcess.data.status;
      // console.timeEnd('apollo');
    },

    selectTab(index) {
      this.updateSelectedTab(index);
    },

    // // functcion to gerate unique id based in timestamp
    // generateId() {
    //   console.log(ObjectID().toHexString());
    //   return ObjectID().toHexString();
    //   // return new Date().getTime();
    // },

    close(index) {
      if (this.tabList.length > 1) {
        this.removeTabByIndex(index);
        if (index <= this.selectedTabIndex) {
          // this.tabList.length(0);
          this.updateSelectedTab(this.selectedTabIndex - 1);
        }
      }
    },

    add() {
      const tabLength = this.tabList.length;
      let tabSketchName = `Aba ${this.newTabCount}`;
      if (tabLength === 0) tabSketchName = 'Aba 1';
      const idGenerated = ObjectID().toHexString();

      this.newTabCount += 1;

      this.newTab.name = tabSketchName;
      this.newTab.parent_id = idGenerated;
      // eslint-disable-next-line no-underscore-dangle
      this.newTab._id = idGenerated;
      this.newTab.version = 1;
      this.newTab.content = this.contentDefault;

      this.addTab({ ...this.newTab });
      // console.log('tab length: ', tabLength);
      this.updateSelectedTab(tabLength);
      this.tab = tabLength;
    },

    duplicate() {
      const idGenerated = ObjectID().toHexString();

      const duplicatedTab = this.newTab;

      duplicatedTab.saved = false;
      duplicatedTab.duplicated = true;
      // eslint-disable-next-line no-underscore-dangle
      duplicatedTab._id = idGenerated;
      duplicatedTab.parent_id = idGenerated;

      this.duplicateTab({
        tab: { ...duplicatedTab },
        indexContextMenu: this.contextMenuSelectedTabIndex,
      });
      // console.log('selected indexxxxxxxxxxxxxxxx: ', this.selectedTabIndex);
      // console.log('CONTEEEEEEEEEEEEEEEEEE',this.contextMenuSelectedTabIndex)

      this.updateSelectedTab(this.contextMenuSelectedTabIndex + 1);
      this.tab = this.contextMenuSelectedTabIndex + 1;
    },

    rename(index) {
      this.setRenamingIndex(null);
      this.setSketchName({ name: this.name, index });
      this.name = '';
    },
  },

  mounted() {
    if (this.tabList.length === 0) {
      this.add();
    }
  },
};
</script>

<style scoped lang="scss">
.content {
  width: 100%;
}

.list-item {
  min-height: 37px;
}

.add-tab {
  align-self: center;
  margin: 9px;
}

.context-menu-btn {
  display: none;
}

.tab-item:hover + .context-menu-btn {
  display: block;
}
</style>
