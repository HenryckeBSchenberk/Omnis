/* eslint-disable no-underscore-dangle */
<template>
  <!-- <v-card class="mb-4" min-height="100px" outlined> -->
  <div>
    <div class="d-flex align-center p-4" v-if="obj">
      <div>
        <div class="d-flex align-center">
          <v-avatar :color="obj.img ? '' : 'primary'" size="90">
            <img v-if="obj.img" :src="obj.img" />
            <span v-else class="text-uppercase">{{ getInitials() }}</span>
          </v-avatar>
          <div class="pl-4 pr-4">
            <span class="text-h6 text-capitalize">{{ obj.name }}</span>
            <div class="text-subtitle-2">{{ obj.description }}</div>
            <div class="font-weight-bold d-flex align-center">
              <div class="text-body-2 mr-1">{{ $t('form.name') }}:</div>
              {{ obj.content.name }}
            </div>
            <div class="font-weight-bold d-flex align-center">
              <div class="text-body-2 mr-1">ID:</div>
              {{ obj._id }}
            </div>
            <!-- <div class="text-body-2">
            {{ $timestampToDate(obj.date) }}
          </div> -->
          </div>
        </div>
      </div>
      <v-spacer></v-spacer>
      <div class="d-flex">
        <v-btn class="mr-5" icon @click="show = !show"
          ><v-icon>{{
            show ? 'mdi-chevron-up' : 'mdi-chevron-down'
          }}</v-icon></v-btn
        >
        <dialog-confirmation
          v-if="dialogDelete"
          @confirm-event="remove"
          @cancel-event="dialogDelete = false"
        ></dialog-confirmation>
        <div>
          <v-menu transition="slide-x-transition" bottom left offset-x>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon v-bind="attrs" v-on="on">
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item
                class="list-item"
                v-for="(item, index) in items"
                :key="index"
                link
                @click="item.function()"
              >
                <v-list-item-title
                  ><v-icon small class="mr-5">mdi-{{ item.btnIcon }}</v-icon
                  >{{ $t(item.title) }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </div>
    </div>
    <v-expand-transition>
      <div v-show="show">
        <!-- <v-divider></v-divider> -->
        <v-card-text>
          <v-data-table
            :headers="headers"
            :items="detailItems"
            hide-default-header
            hide-default-footer
          >
            <template v-slot:[`item.field`]="{ item }">
              <div class="font-weight-bold text-capitalize">
                {{ item.field }}
              </div>
            </template></v-data-table
          ></v-card-text
        >
        <v-divider></v-divider>
      </div>
    </v-expand-transition>
  </div>
  <!-- </v-card> -->
</template>

<script>
import { mapActions } from 'vuex';
import DialogConfirmation from '@/components/settings/DialogConfirmation.vue';

export default {
  components: { DialogConfirmation },
  props: {
    obj: Object,
  },
  data() {
    return {
      show: false,
      dialogDelete: false,
      headers: [
        {
          text: 'field',
          value: 'field',
        },
        {
          text: 'value',
          value: 'value',
        },
      ],
      items: [
        {
          title: 'buttons.edit',
          btnIcon: 'pencil',
          function: this.edit,
        },
        {
          title: 'buttons.remove',
          btnIcon: 'delete',
          function: this.dialog,
        },
      ],
    };
  },

  computed: {
    detailItems() {
      return Object.keys(this.obj.content).map((key) => ({
        field: key,
        value: this.obj.content[key],
      }));
    },
  },

  methods: {
    ...mapActions({
      updateUser: 'auth/updateUser',
    }),

    getInitials() {
      return this.user?.name?.charAt(0);
    },

    remove() {
      // eslint-disable-next-line no-underscore-dangle
      this.$emit('remove-obj', this.obj._id);
      this.dialogDelete = false;
    },

    edit() {
      this.$emit('edit-obj', this.obj);
    },

    dialog() {
      this.dialogDelete = true;
    },
  },
};
</script>

<style>
</style>
