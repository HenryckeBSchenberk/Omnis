<template>
  <div class="object-register mt-11">
    <v-form ref="form" v-model="valid" lazy-validation>
      <div v-for="item in updated_items" :key="item.field">
        <v-text-field
          v-model="obj[item.field]"
          @click:append="dellItem(item)"
          :append-icon="item.field == 'name' ? '' : 'mdi-trash-can'"
          :label="
            (item.field == 'name' ? $t('form.' + item.field) : item.field) + '*'
          "
          :rules="[(v) => !!v || $t('form.required') + '!']"
          outlined
          rounded
          dense
        >
        </v-text-field>
      </div>
      <!-- 2 Flexible input fields for add new item on items list -->
      <v-divider class="mt-4"></v-divider>
      <div class="d-flex mt-4">
        <v-text-field
          class="mr-4"
          v-model="newItem"
          :label="$t('form.key')"
          placeholder=""
          outlined
          rounded
          dense
          @keyup.enter="addItem()"
        >
        </v-text-field>
        <v-text-field
          class="mr-4"
          v-model="newItemValue"
          :label="$t('form.value')"
          placeholder=""
          outlined
          rounded
          dense
          @keyup.enter="addItem()"
        >
        </v-text-field>
        <v-btn color="primary" @click="addItem()" rounded>
          {{ $t('buttons.add') }}
        </v-btn>
      </div>

      <v-divider class="mt-4"></v-divider>
      <div class="d-flex mt-4">
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="validate()" rounded>
          {{ edit ? $t('buttons.edit') : $t('buttons.register') }}
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script>
import gql from 'graphql-tag';

const LIST_VARIABLES = gql`
  query LIST_VARIABLES {
    get_variable_list {
      _id
      name
    }
  }
`;

const LIST_MATRIX = gql`
  query LIST_MATRIX {
    get_matrix_list {
      _id
      name
    }
  }
`;

const ADD_OBJECT = gql`
  mutation ADD_OBJECT($content: JSON!) {
    create_object(input: { content: $content })
  }
`;

const UPDATE_OBJ = gql`
  mutation UPDATE_OBJ($_id: ID!, $content: JSON!) {
    update_object(_id: $_id, input: { content: $content })
  }
`;

export default {
  name: 'ObjectRegister',
  props: {
    items: Array,
    id: String,
    edit: Boolean,
  },

  data() {
    return {
      valid: true,
      formHasErrors: false,
      obj: {},
      autocompleteInclude: ['object', 'sketch'],
      newItem: '',
      newItemValue: '',
      new_items: [],
    };
  },

  apollo: {
    get_variable_list: LIST_VARIABLES,
    get_matrix_list: LIST_MATRIX,
  },

  created() {
    this.items.forEach((item) => {
      this.obj[item.field] = item.value;
    });
  },

  computed: {
    updated_items() {
      return [...this.items, ...this.new_items];
    },
  },
  methods: {
    rules() {
      return {
        required: (value) => !!value || this.$t('form.required'),
      };
    },

    dellItem(item) {
      console.log('dellItem', item);
      this.new_items.splice(this.items.indexOf(item), 1);
    },
    addItem() {
      // After add the new item, when they are updated, nothing occurs, why?
      if (this.newItem && this.newItemValue) {
        this.obj[this.newItem] = this.newItemValue;
        this.new_items.push({ field: this.newItem, title: this.newItem });
        this.newItem = '';
        this.newItemValue = '';
      }
    },

    validate() {
      if (this.$refs.form.validate()) {
        if (this.edit) {
          this.aditObject(this.obj);
        } else {
          this.addObject(this.obj);
        }
      } else {
        this.formHasErrors = true;
      }
    },

    async addObject(obj) {
      console.log('input', obj);

      await this.$apollo
        .mutate({
          mutation: ADD_OBJECT,
          variables: {
            content: obj,
          },
        })

        .then(() => {
          this.$alertFeedback(this.$t('alerts.updateUserSuccess'), 'success');
          this.$emit('refetch');
          this.$refs.form.reset();
        })

        .catch((error) => {
          this.$alertFeedback(this.$t('alerts.updateUserFail'), 'error', error);
        });
    },

    async aditObject(obj) {
      console.log('edit2', obj);
      await this.$apollo
        .mutate({
          mutation: UPDATE_OBJ,
          variables: {
            _id: this.id,
            content: obj,
          },
        })

        .then(() => {
          this.$emit('refetch');
          this.$alertFeedback(this.$t('alerts.updateObjSuccess'), 'success');
          this.$router.back();
        })

        .catch((error) => {
          this.isLoading = false;
          this.$alertFeedback(this.$t('alerts.updateObjFail'), 'error', error);
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.object-register {
  max-width: 550px;

  .field {
    padding: 1.5rem 0;
  }
}
</style>
