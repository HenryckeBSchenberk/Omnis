<template>
  <div class="object-register mt-11">
    <v-form
      v-model="isValid"
      ref="form"
      rounded
      max-width="700px"
      lazy-validation
    >
      <div v-for="(item, index) in items" :key="index">
        <v-text-field
          v-if="!autocompleteInclude.includes(item.field)"
          :label="$t('form.' + item.field) + (item.required ? '*' : '')"
          placeholder=""
          outlined
          rounded
          v-model="obj[item.field]"
          dense
          :rules="item.required ? [rules().required] : [true]"
          @keyup.enter="colorShow = false"
        >
        </v-text-field>
        <v-autocomplete
          class="select"
          v-if="autocompleteInclude.includes(item.field)"
          :label="$t('form.' + item.field) + (item.required ? '*' : '')"
          rounded
          outlined
          v-model="obj[item.field]"
          :rules="item.required ? [rules().required] : [true]"
          :items="item.field == 'object' ? get_object_list : get_sketch_list"
          :item-text="item.field == 'object' ? 'content.name': 'name'"
          item-value="_id"
          return-object
        ></v-autocomplete>
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

const LIST_SKETCH = gql`
  query LIST_SKETCH {
    get_sketch_list {
      _id
      name
    }
  }
`;

const LIST_OBJECT = gql`
  query LIST_OBJECT {
    get_object_list {
      _id
      content
    }
  }
`;

const LIST_MATRIX = gql`
  query LIST_MATRIX {
    get_matrix_list {
      _id
      content
    }
  }
`;

const ADD_PROCESS = gql`
  mutation ADD_PROCESS(
    $sketch: DBREF_sketch
    $description: String
    $img: String
    $name: String
    $object: DBREF_object
  ) {
    create_process(
      input: {
        description: $description
        sketch: $sketch
        img: $img
        name: $name
        object: $object
      }
    )
  }
`;

const UPDATE_PROCESS = gql`
  mutation UPDATE_PROCESS(
    $_id: ID!
    $description: String
    $img: String
    $name: String
    $sketch: DBREF_sketch
    $object: DBREF_object
  ) {
    update_process(
      _id: $_id
      input: {
        description: $description
        img: $img
        name: $name
        sketch: $sketch
        object: $object
      }
    )
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
      isValid: true,
      obj: {},
      autocompleteInclude: ['object', 'sketch'],
    };
  },

  beforeMount() {
    this.items.forEach((item) => {
      this.generateObj(item);
    });
  },

  apollo: {
    get_sketch_list: LIST_SKETCH,
    get_object_list: LIST_OBJECT,
    get_matrix_list: LIST_MATRIX,
  },

  methods: {
    rules() {
      return {
        required: (value) => !!value ||  this.$t('form.required'),
      };
    },

    generateObj(item) {
      this.obj[item.field] = item.value;
    },

    validate() {
      if (this.$refs.form.validate()) {
        if (this.edit) {
          this.editProcess(this.obj);
        } else {
          this.addProcess(this.obj);
        }
      } else {
        this.formHasErrors = true;
      }
    },

    async addProcess(obj) {
      await this.$apollo
        .mutate({
          mutation: ADD_PROCESS,
          variables: {
            description: obj.description,
            img: obj.img,
            name: obj.name,
            sketch: obj.sketch,
            object: obj.object,
          },
        })

        .then(() => {
          // Result
          this.$emit('refetch');
          this.$alertFeedback(this.$t('alerts.updateUserSuccess'), 'success');
          this.$refs.form.reset();
        })

        .catch((error) => {
          // Error
          this.$alertFeedback(this.$t('alerts.updateUserFail'), 'error', error);
        });
    },
    async editProcess(obj) {
      await this.$apollo
        .mutate({
          mutation: UPDATE_PROCESS,
          variables: {
            // eslint-disable-next-line no-underscore-dangle
            _id: this.id,
            description: obj.description,
            img: obj.img,
            name: obj.name,
            sketch: obj.sketch,
            object: obj.object,
          },
        })

        .then(() => {
          // Result
          this.$emit('refetch');
          this.$alertFeedback(
            this.$t('alerts.updateProcessSuccess'),
            'success',
          );
          this.$router.back();
        })

        .catch((error) => {
          // Error
          this.isLoading = false;
          this.$alertFeedback(
            this.$t('alerts.updateProcessFail'),
            'error',
            error,
          );
          // We restore the initial user input
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
