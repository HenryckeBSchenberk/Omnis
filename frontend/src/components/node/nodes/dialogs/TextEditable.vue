<template>
  <div v-if="!editMode" class="d-flex justify-space-between full-width">
    {{ text }}
    <v-btn
      color="grey"
      style="float: right"
      dark
      icon
      x-small
      @click="editMode = true"
    >
      <v-icon>mdi-pencil</v-icon>
    </v-btn>
  </div>
  <div v-else v-click-outside="clickOutside" class="full-width">
    <v-text-field
      v-model="textCopy"
      dense
      hide-details=""
      autofocus
      @keyup.enter="save"
      autocomplete="off"
    >
      <template v-slot:append>
        <v-btn icon x-small color="primary" @click="save">
          <v-icon>mdi-check</v-icon>
        </v-btn>
      </template>
    </v-text-field>
  </div>
</template>

<script>
export default {
  props: ['text'],
  data() {
    return {
      editMode: false,
      textCopy: null,
    };
  },
  created() {
    this.textCopy = `${this.text}`;
  },
  methods: {
    save() {
      this.$emit('changeText', this.textCopy);
      this.editMode = false;
    },
    clickOutside() {
      this.editMode = false;
    },
  },
};
</script>
<style scoped>
.full-width {
  width: 100%;
}
</style>
