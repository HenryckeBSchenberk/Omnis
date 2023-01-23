<template>
  <div class="main">
    <div class="d-flex align-">
      <v-autocomplete
        v-model="model"
        :items="items"
        :search-input.sync="search"
        auto-select-first
        clearable
        :item-text="itemSearch"
        class="mx-4 mb-4 search"
        rounded
        filled
        dense
        prepend-inner-icon="mdi-magnify"
        hide-no-data
        hide-details
        :placeholder="$t('buttons.search')"
      ></v-autocomplete>
      <v-spacer></v-spacer>
      <div class="sort d-flex justify-center align-center">
        <v-btn class="mr-4" small icon @click="items.reverse()">
          <v-icon>mdi-swap-vertical</v-icon>
        </v-btn>
        <div class="">
          {{ $t('list.sortBy') }}:
          <span class="font-weight-bold">{{
            dropdown.value ? $t(translatePath + '.' + dropdown.value) : '  '
          }}</span>
        </div>

        <v-menu bottom offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn small text icon v-bind="attrs" v-on="on">
              <v-icon>mdi-chevron-down</v-icon>
            </v-btn>
          </template>
          <!-- 
              verifica items[0] antes de tentar pegar as 'chaves' dos dicionário
              evitando que o Object.keys() resulte em erro.
           -->
          <v-list>
            <v-list-item
              @click="sort(item)"
              link
              v-for="(item, index) in Object.keys(items[0])"
              :key="index"
              v-show="!fieldsIgnore.includes(item)"
            >
              <v-list-item-title>{{
                $t(translatePath + '.' + item)
              }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
    </div>
    <div v-for="(item, index) in itemsCopy" :key="index">
      <slot name="itemList" :data="item"></slot>
    </div>
  </div>
</template>

<script>
// import SettingsListItemUser from './SettingsListItemUser.vue';

export default {
  //   components: { SettingsListItemUser },
  props: {
    items: {
      type: Array,
      default: () => [{}],
    },
    itemSearch: {
      type: String,
      default: 'title',
    },
    fieldsIgnore: {
      type: Array,
      default: () => [],
    },
    translatePath: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      search: null,
      show: false,
      model: null,
      dropdown: {
        value: '',
        text: '',
      },
    };
  },

  watch: {
    search(newValue, oldValue) {
      if (!newValue) {
        this.makeCopy();
      }
    },
  },

  computed: {
    itemsCopy() {
      return this.makeCopy();
    },
  },

  methods: {
    makeCopy() {
      if (this.search) {
        return this.items.filter((value) => {
          return value[this.itemSearch] === this.search;
        });
      }
      return this.items;
    },

    filter() {
      if (this.itemsCopy.length !== 0) {
        this.itemsCopy = this.items.filter((value) => {
          return value[this.itemSearch] === this.search;
        });
      }
    },

    sort(item) {
      this.dropdown.value = item;
      this.dropdown.text = this.$t(`settings.users.fields.${item}`);

      // console.log(item, typeof item);

      this.itemsCopy.sort((a, b) => {
        let fa = a[item];
        let fb = b[item];

        if (typeof fa === 'string') fa.toLowerCase();
        if (typeof fb === 'string') fb.toLowerCase();

        if (fa < fb) {
          return -1;
        }
        if (fa > fb) {
          return 1;
        }
        return 0;
      });
    },

    change(value) {
      // this.$emit('selected', value);
      this.$emit('update:selected', this.$event.target.checked);
    },
  },
};
</script>

<style scoped>
.main {
  max-width: 900px;
}
.search {
  max-width: 300px;
}
.sort {
  height: 2.3rem;
}
</style>
