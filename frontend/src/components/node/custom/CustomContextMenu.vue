<template>
  <div class="text-center" :key="componentKey">
    <v-menu
      v-model="value"
      :position-x="x"
      :position-y="y"
      absolute
      offset-y
      eager
      :close-on-click="false"
      :close-on-content-click="false"
      v-click-outside="{
        handler: onClickOutside,
        include: include,
      }"
    >
      <v-card
        :width="width"
        class="included"
        transition="scale-transition"
        origin="center center"
        dark
      >
        <!-- <v-card-title>
          <span class="headline">Adicionar Node</span>
          <v-spacer></v-spacer>
          <v-text-field
            outlined
            label="Search Node Type"
            dense
            hide-details
            v-model="search"
            clearable
            autofocus
            @keypress.enter="keyPressed"
          ></v-text-field>
          <v-btn class="ml-2" dark @click="toggleSize">
            <v-icon>{{maxed ? 'mdi-window-minimize' : 'mdi-window-maximize'}}</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider> -->

        <v-row>
          <v-col>
            <v-list>
              <v-list-group
                v-for="(category, index) in categories"
                :key="index"
              >
                <template v-slot:activator>
                  <v-list-item-content>
                    <v-list-item-title v-text="category"></v-list-item-title>
                  </v-list-item-content>
                </template>

                <v-list-item
                  v-for="(item, index2) in descriptionsList"
                  @mouseenter="updateHoverItem(item)"
                  @click="addNode()"
                  :key="index2"
                  v-if="item.category == category"
                  link
                >
                  <v-list-item-icon>
                    <v-icon
                      v-text="`mdi-${item.icon}`"
                    ></v-icon> </v-list-item-icon
                  ><link rel="stylesheet" href="" />

                  <v-list-item-content>
                    <v-list-item-title v-text="item.name"></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-group>
            </v-list>
          </v-col>
          <v-col v-if="hoveredItem" class="mt-4">
            <div class="text-h5">{{ hoveredItem.name }}</div>
            <v-divider></v-divider>
            <p class="text-subtitle-1 text--grey lighten-4">
              {{ hoveredItem.text }}
            </p>
            <br />
            <div class="font-italic text-subtitle-1 text--grey lighten-5">
              Exemplo:
            </div>
            <p class="text--grey lighten-4">{{ hoveredItem.examples }}</p>
          </v-col>
        </v-row>
        <!-- <v-card-text class="pb-0">
          <v-row v-if="nodeListFiltered && nodeListFiltered.length !== 0">
            <v-col
              :cols="cols"
              class="pb-0"
              style="max-height: 300px; overflow: scroll"
            >
              <h4 style="text-align: left">Nodes</h4>
              <v-chip-group
                active-class="primary--text"
                column
                v-model="selected"
              >
                <v-chip
                  v-for="(node, index) in nodeListFiltered"
                  :key="index"
                  :small="!maxed"
                  @keyup.enter="keyPressedItem(node, index)"
                >
                  {{ node.type }}
                </v-chip>
              </v-chip-group>
              <v-divider v-if="templates.length !== 0"></v-divider>
              <h4 v-if="templates.length !== 0" style="text-align: left">
                Templates
              </h4>
              <v-chip-group
                active-class="primary--text"
                column
                v-model="selectedTemplate"
              >
                <v-chip
                  v-for="(template, index) in templates"
                  :key="index"
                  :small="!maxed"
                >
                  {{ template.name }}
                </v-chip>
              </v-chip-group>
            </v-col>
            <v-col
              class="pb-0"
              style="text-align: left; max-height: 300px; overflow: scroll"
            >
              <h2 class="mb-3">{{ selectedTitle }}</h2>
              <p v-html="selectedDescr" style="font-size: 16px"></p>
              <v-spacer></v-spacer>
              <h4 v-if="selectedTags.length !== 0" style="text-align: left">
                Tags
              </h4>
              <v-chip
                label
                small
                :key="tag"
                v-for="tag in selectedTags"
                class="mr-1 mb-1"
                style="cursor: default"
                @click="search = tag"
                :class="{ tagselected: tag === search }"
              >
                <v-icon left> mdi-tag-text-outline </v-icon>
                {{ tag }}
              </v-chip>
            </v-col>
          </v-row>
        </v-card-text> -->
        <!-- <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="green" @click="addNode"> Add Node </v-btn>
        </v-card-actions> -->
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import Home from '@/views/Home.vue';
import { Components } from '@baklavajs/plugin-renderer-vue';
import {
  getDescription,
  getTags,
  getCategoryList,
  descriptions,
} from '@/components/node/nodes/nodeDescription';

export default {
  components: { Home },
  extends: Components.ContextMenu,
  inject: ['plugin'],
  data: () => ({
    nodeList: null,
    valueCopy: false,
    selected: 0,
    selectedTemplate: null,
    search: '',
    maxed: false,
    addList: [],
    templates: [],
    componentKey: 0,
    hoveredItem: null,
    descriptionsList: descriptions,
    categories: getCategoryList(),
  }),
  methods: {
    updateHoverItem(item) {
      this.hoveredItem = item;
    },

    traverseSubmenues(submenu) {
      if (submenu.submenu) {
        submenu.submenu.forEach((submenu) => {
          this.traverseSubmenues(submenu);
        });
      } else {
        this.nodeList.push({
          type: submenu.label,
          callstr: submenu.value,
          description: getDescription(submenu.label),
          tags: getTags(submenu.label),
        });
      }
    },
    include() {
      return [document.querySelector('.included')];
    },

    add() {},

    addNode() {
      if (this.selected != null) {
        this.onChildClick(`addNode:${this.hoveredItem.type}`);
      } else this.addTemplate();
    },
    addTemplate() {
      const template = this.templates[this.selectedTemplate];

      template.position.x = this.x / this.plugin.scaling - this.plugin.panning.x;
      template.position.y = this.y / this.plugin.scaling - this.plugin.panning.y;

      this.$store.commit('createNodeFromTemplate', template);
      this.onClickOutside(undefined);
    },
    fetchTemplates() {
      // let loadTemplateUrl = `${apiBaseUrl}/node-templates/all`;
      // this.axios.get(loadTemplateUrl)
      // .then((response) => {
      //   this.templates = response.data;
      // });
    },
    keyPressed(event) {
      this.addNode();
    },
    keyPressedItem(node, index) {
      if (this.selected === index) this.addNode();
      else this.selected = index;
    },
    toggleSize() {
      this.maxed = !this.maxed;
      this.forceRerender();
    },
    forceRerender() {
      this.componentKey += 1;
    },
  },
  watch: {
    value() {
      this.nodeList = [];
      this.addList = [];
      this.traverseSubmenues(this.items[0]);
      this.fetchTemplates();
    },
    items() {
      this.nodeList = [];
      this.traverseSubmenues(this.items[0]);
    },
    search(newValue) {
      this.selected = 0;
      if (newValue === null) this.search = '';
    },
    selected(newValue) {
      if (newValue != null) {
        this.selectedTemplate = null;
      }
    },
    selectedTemplate(newValue) {
      if (newValue != null) {
        this.selected = null;
      }
    },
  },
  computed: {
    nodeListFiltered() {
      if (this.nodeList) {
        return this.nodeList.filter(
          (node) => node.type.includes(this.search)
            || node.tags.some((tag) => tag.includes(this.search)),
        );
      }
      return null;
    },

    // categories() {
    //   console.log(getCategoryList());
    //   return getCategoryList();
    // },

    width() {
      return this.maxed ? 1200 : 600;
    },
    cols() {
      return this.maxed ? 4 : 6;
    },
    selectedTitle() {
      return (
        this.nodeListFiltered[this.selected]?.type
        || `Template: ${this.templates[this.selectedTemplate]?.name}`
      );
    },
    selectedDescr() {
      const nodeDescription = this.nodeListFiltered[this.selected]?.description;
      if (nodeDescription) return nodeDescription; // Guard-clause for node case

      const templateSettings = this.templates[
        this.selectedTemplate
      ]?.options.find((option) => option[0] === 'settings');
      if (templateSettings && templateSettings[1]?.notes) { return templateSettings[1]?.notes; }

      return 'No description provided';
    },
    selectedTags() {
      return this.nodeListFiltered[this.selected]?.tags || [];
    },
  },
};
</script>

<style>
.tagselected {
  background-color: lightpink !important;
}
</style>
