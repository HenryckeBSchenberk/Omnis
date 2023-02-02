<template>
  <div v-if="get_sketch_list" class="d-flex">
    <v-data-table
      :headers="headers"
      :items="get_sketch_list"
      sort-by="_id"
      :sort-desc="true"
      class="elevation-1 table-warper"
      :footer-props="{
        itemsPerPageText: 'Arquivos por página:',
        itemsPerPageAllText: 'Todos',
      }"
    >
      <template v-slot:item.author="{ item }">
        <v-tooltip top allow-overflow nudge-top>
          <template v-slot:activator="{ on }">
            <div class="user" v-on="on">
              <v-avatar size="40">
                <img
                  :src=" item.created_by.avatar_image"
                  alt="avatar"
                  class="avatar"
                />
              </v-avatar>
            </div>
          </template>
          <span>{{ item.created_by.first_name.toLowerCase()}}</span>
        </v-tooltip>
      </template>

      <template v-slot:item.name="{ item }" class="name">
        <div
          v-if="!(selectedId == item._id && editNameMode)"
          @dblclick="editTextIntention(item._id, 'name', item.name)"
        >
          {{ item.name }}
          <v-icon v-if="runningFileId == item._id" small color="green"
            >mdi-play-circle</v-icon
          >
        </div>
        <div v-else class="mb-n5 mt-n6">
          <v-text-field
            :append-outer-icon="item.name ? 'mdi-check' : null"
            @click:append-outer="edit(item._id, item.name, item.description)"
            autofocus
            :value="item.name"
            v-model="item.name"
            @keyup.enter="
              item.name != ''
                ? edit(item._id, item.name, item.description)
                : item.name
            "
            single-line
            full-width
          ></v-text-field>
        </div>
        <!-- <span v-else>{{ item.title }}</span> -->
      </template>

      <template v-slot:item.description="{ item }">
        <div
          v-if="!(selectedId == item._id && editDescriptionMode)"
          @dblclick="
            editTextIntention(item._id, 'description', item.description)
          "
        >
          {{ item.description }}
        </div>
        <div v-else class="mb-n5 mt-n6">
          <v-text-field
            :append-outer-icon="item.description ? 'mdi-check' : null"
            @click:append-outer="edit(item._id, item.name, item.description)"
            autofocus
            :value="item.description"
            v-model="item.description"
            @keyup.enter="
              item.description != ''
                ? edit(item._id, item.name, item.description)
                : item.description
            "
            single-line
            full-width
          ></v-text-field>
        </div>
        <!-- <span v-else>{{ item.title }}</span> -->
      </template>

      <template v-slot:item.lastAccess="{ item }">
        {{ timestampToData(item.updated_at) }}
      </template>
      <template v-slot:item.actions="{ item }">
        <!-- <v-icon small class="mr-2" @click="editItem(item)"> mdi-pencil </v-icon>
        <v-icon small @click="deleteItem(item)"> mdi-delete </v-icon> -->
        <v-menu offset-y style="max-width: 600px">
          <template v-slot:activator="{ on, attrs }">
            <v-icon v-on="on" v-bind="attrs" @click="selectedId = item._id">
              mdi-dots-vertical
            </v-icon>
          </template>

          <v-list>
            <v-list-item
              @click="option.function(index)"
              v-for="(option, index) in contextMenuList"
              :key="index.title"
            >
              <v-list-item-title
                ><v-icon small class="mr-5">mdi-{{ option.btnIcon }}</v-icon
                >{{ option.title }}
              </v-list-item-title>
            </v-list-item>
            <v-list-item @click="dialogDelete = true">
              <v-list-item-title>
                <v-icon small class="mr-5">mdi-delete</v-icon>Deletar
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
      <template v-slot:no-data>
        <v-btn rounded color="primary" @click="initialize"> recarregar </v-btn>
      </template>
    </v-data-table>
    <dialog-confirmation
      v-if="dialogDelete"
      del
      @confirm-event="del"
      @cancel-event="dialogDelete = false"
    >
        </dialog-confirmation>
  </div>
</template>

<script>
import gql from 'graphql-tag';
import { mapActions } from 'vuex';
import DialogConfirmation from '@/components/settings/DialogConfirmation.vue';

const GET_SKETCH_LIST = gql`
  query {
    get_sketch_list {
      _id
      version
      name
      description
      node_qtd
      edited_by {
        first_name
        avatar_image
      }
      created_by {
        first_name
        avatar_image
      }
      updated_at
    }
  }
`;

const SAVE_NODE_SHEET = gql`
  mutation ($id: ID!, $name: String, $description: String) {
    update_sketch(_id: $id, input: { name: $name, description: $description })
  }
`;

const DELETE_NODE_SHEET = gql`
  mutation ($id: ID!) {
    delete_sketch(_id: $id)
  }
`;

const DUPLICATE_NODE_SHEET = gql`
  mutation ($id: ID!) {
    duplicate_sketch(_id: $id)
  }
`;

const GET_CONFIG = gql`
  query ($_id: ID!) {
    get_sketch_item(_id: $_id) {
      _id
      name
      description
      version
      node_qtd
      author
      updated_at
      parent_id
      content
      saved
      duplicated
    }
  }
`;

export default {
  components: { DialogConfirmation },
  data() {
    return {
      dialog: false,
      dialogDelete: false,
      headers: [
        { text: 'Autor', value: 'author' },
        {
          text: 'Nome',
          align: 'start',
          value: 'name',
        },
        { text: 'Descrição', value: 'description' },
        // { text: 'Versão', value: 'version' },
        // { text: 'Qtd. nó', value: 'node_qtd' },
        
        { text: 'ID', value: '_id' },
        { text: 'Ultima Alteração', value: 'lastAccess' },
        { text: 'Ações', value: 'actions', sortable: false },
      ],
      // files: [],
      runningFileId: 16530682866630,
      editedIndex: -1,
      selectedId: null,
      renamingIndex: null,
      editNameMode: false,
      editDescriptionMode: false,
      originalFieldText: null,
      contextMenuList: [
        {
          title: 'Abrir',
          btnIcon: 'folder-open',
          function: this.open,
          enabled: true,
        },
        {
          title: 'Duplicar',
          btnIcon: 'content-duplicate',
          function: this.duplicate,
          enabled: true,
        },
        // {
        //   title: 'Editar',
        //   btnIcon: 'pencil',
        //   function: this.edit,
        //   enabled: true,
        // },
        // {
        //   title: 'Renomear',
        //   btnIcon: 'form-textbox',
        //   function: this.rename,
        //   enabled: true,
        // },
        // {
        //   title: 'Deletar',
        //   btnIcon: 'delete',
        //   function: this.del,
        //   enabled: true,
        // },
      ],
    };
  },

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'New Item' : 'Edit Item';
    },
  },

  created() {
    this.initialize();
  },

  apollo: {
    get_sketch_list: {
      query: GET_SKETCH_LIST,
      fetchPolicy: 'network-only',
      // nextFetchPolicy: 'network-only',
    },
  },

  methods: {
    ...mapActions('node', ['loadTabId']),

    initialize() {
      this.$apollo.queries.get_sketch_list.refetch();
      // this.files = [
      //   {
      //     name: 'Pega de conectores',
      //     description:
      //       'Rotina Para pega de conectores, no gabarito e a colocação dele nos painéis',
      //     nodeQtd: 6,
      //     author: 'Rodrigo Gomes',
      //     lastAccess: '1653080955',
      //     id: '16530682866630',
      //   },
      // ];
    },

    async edit(id, name, description) {
      this.editNameMode = false;
      this.editDescriptionMode = false;
      this.selectedId = null;

      await this.$apollo
        .mutate({
          mutation: SAVE_NODE_SHEET,
          variables: {
            id,
            name,
            description,
          },
        })
        .then(() => {
          // Result
          this.$apollo.queries.get_sketch_list.refetch();
          this.$alertFeedback('seu arquivo foi editado com sucesso', 'success');
          // this.isLoading = false;
          // this.setSaved(this.selectedTabIndex);
        })

        .catch((error) => {
          // Error
          this.isLoading = false;
          console.error('Não foi editar o arquivo \n', error);
          this.$alertFeedback(
            'Não foi possível editar o arquivo',
            'error',
            error
          );

          // We restore the initial user input
        });
    },

    async open() {
      console.log('open', this.selectedId)
      await this.$apollo
        .query({
          query: GET_CONFIG,
          variables: {
            _id: this.selectedId,
          },
        })
        .then((data) => {
          // Result
          this.loadTabId(data.data.get_sketch_item);
          this.dialog = true;
          this.$emit('close-dialog');
          // this.isLoading = false;
          // this.setSaved(this.selectedTabIndex);
        })

        .catch((error) => {
          // Error
          this.isLoading = false;
          console.error('Não foi possível carregar o arquivo \n', error);
          this.$alertFeedback(
            'Não foi possível carregar o arquivo',
            'error',
            error
          );

          // We restore the initial user input
        });
    },

    async del() {
      this.dialog = true;
      const id = this.selectedId;
      await this.$apollo
        .mutate({
          mutation: DELETE_NODE_SHEET,
          variables: {
            id,
          },
        })

        .then(() => {
          // Result
          this.$apollo.queries.get_sketch_list.refetch();
          this.$alertFeedback(
            'Seu arquivo foi deletado com sucesso',
            'success'
          );
          // this.isLoading = false;
          // this.setSaved(this.selectedTabIndex);
          this.dialogDelete = false;
        })

        .catch((error) => {
          // Error
          this.isLoading = false;
          console.error('Não foi possível deletar o arquivo \n', error);
          this.$alertFeedback(
            'Não foi possível deletar o arquivo',
            'error',
            error
          );

          // We restore the initial user input
        });
    },

    async duplicate() {
      const id = this.selectedId;
      await this.$apollo
        .mutate({
          mutation: DUPLICATE_NODE_SHEET,
          variables: {
            id,
          },
        })

        .then(() => {
          // Result
          this.$apollo.queries.get_sketch_list.refetch();
          this.$alertFeedback(
            'Seu arquivo foi duplicado com sucesso',
            'success'
          );
        })

        .catch((error) => {
          // Error
          this.isLoading = false;
          console.error('Não foi possível duplicar o arquivo \n', error);
          this.$alertFeedback(
            'Não foi possível duplicado o arquivo',
            'error',
            error
          );

          // We restore the initial user input
        });
    },

    editTextIntention(id, field, text) {
      this.originalFieldText = text;
      this.selectedId = id;
      switch (field) {
        case 'name':
          this.editNameMode = true;
          console.log('editNameMode', this.editNameMode);
          break;
        case 'description':
          this.editDescriptionMode = true;
          break;
        default:
      }
    },

    rename() {
      console.log('rename');
      this.editNameMode = false;
      this.editDescriptionMode = false;
      this.selectedId = null;
    },

    timestampToData(timestamp) {
      const d = new Date(timestamp * 1000);
      const options = {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
        hour12: true,
      };

      return new Intl.DateTimeFormat('pt-BR', options).format(d);
    },
  },
};
</script>
<style lang="scss">
.table-warper {
  width: 100%;
  height: 100%;
}
.user {
  display: flex;
  align-items: center;
  width: 100%;
}
</style>
