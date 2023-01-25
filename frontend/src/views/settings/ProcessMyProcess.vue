<template>
  <div class="mt-11">
    <router-view @refetch="refetch()" :items="model"> </router-view>
    <div v-if="$router.currentRoute.name == 'myProcess'">
      <settings-items
        :title="$t('settings.process.process.add')"
        :subtitle="$t('settings.process.process.subtitle')"
        icon="cube"
        divider-list
        path="myProcess/add"
      ></settings-items>

      <settings-title>{{ $t('settings.process.process.list') }}</settings-title>

      <settings-list
        class="mt-4"
        :items="get_process_list"
        item-search="name"
        :fields-ignore="fieldsToIgnore"
        translate-path="form"
      >
        <template #itemList="itemList">
          <settings-list-item-process
            @remove-obj="remove"
            @edit-obj="edit"
            :obj="itemList.data"
          ></settings-list-item-process>
          <v-divider></v-divider>
        </template>
      </settings-list>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag';
import SettingsItems from '@/components/settings/SettingsItems.vue';
import SettingsList from '@/components/settings/SettingsList/SettingsList.vue';
import SettingsTitle from '@/components/settings/SettingsTitle.vue';
import SettingsListItemProcess from '@/components/settings/SettingsList/SettingsListItemProcess.vue';

const LIST_PROCESS = gql`
  query LIST_PROCESS {
    get_process_list {
      name
      _id
      created_at
      created_by {
        first_name
        last_name
      }
      date
      description
      edited_by {
        first_name
        last_name
      }
      img
      last_played
      sketch {
        name
        _id
      }
      updated_at
      object {
        _id
        content
      }
    }
  }
`;

const REMOVE_PROCESS = gql`
  mutation REMOVE_PROCESS($_id: ID!) {
    delete_process(_id: $_id)
  }
`;

export default {
  components: {
    SettingsItems,
    SettingsList,
    SettingsListItemProcess,
    SettingsTitle,
  },
  data() {
    return {
      objToEdit: {},
      editDialog: false,
      fieldsToIgnore: [
        '__typename',
        '_id',
        'img',
        'created_at',
        'created_by',
        'edited_by',
        'updated_at',
        'last_played',
        'date',
      ],
      requireFields: ['name', 'sketch'],
    };
  },

  computed: {
    model() {
      const list = this.objToEdit;
      if (list) {
        // console.log('lista', list);
        const objList = [
          {
            field: 'name',
            value: list.name,
            title: 'name',
            required: true,
          },
          {
            field: 'description',
            value: list.description,
            title: 'description',
          },
          {
            field: 'sketch',
            value: list.sketch,
            title: 'sketch',
            required: true,
          },
          {
            field: 'object',
            value: list.object,
            title: 'object',
          },
          {
            field: 'img',
            value: list.img,
            title: 'img',
          },
        ];
        return objList;
      }
      return [];
    },
  },

  apollo: {
    // Simple query that will update the 'hello' vue property
    get_process_list: LIST_PROCESS,
  },

  methods: {
    refetch() {
      this.$apollo.queries.get_process_list.refetch();
    },

    async remove(_id) {
      console.log('remove', _id);
      await this.$apollo
        .mutate({
          mutation: REMOVE_PROCESS,
          variables: {
            _id,
          },
        })
        .then(() => {
          // Result
          this.$apollo.queries.get_process_list.refetch();
          this.$alertFeedback(this.$t('alerts.deleteSuccess'), 'success');
          // this.isLoading = false;
          // this.setSaved(this.selectedTabIndex);
        })
        .catch((error) => {
          // Error
          this.isLoading = false;
          this.$alertFeedback(this.$t('alerts.deleteFail'), 'error', error);
          // We restore the initial user input
        });
    },

    edit(obj) {
      const newObject = [];

      Object.entries(obj).forEach((a) => {
        if (!this.fieldsToIgnore.includes(a[0])) {
          console.log(a[0], a[1]);
          newObject.push({
            field: a[0],
            value: a[1],
            title: a[0],
          });
          if (this.requireFields.includes(a[0])) newObject.at(-1).required = true;
        }
      });

      this.$router.push({
        name: 'processEdit',
        params: {
          items: newObject,
          // eslint-disable-next-line no-underscore-dangle
          id: obj._id, // or anything you want
          edit: true,
        },
      });
    },
  },
};
</script>

<style>
</style>
