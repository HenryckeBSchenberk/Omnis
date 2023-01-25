export default {
    namespaced: true,
    state: {
        object_id: null,
    },

    getters: {
        getObjectID: state => state.object_id,
    },

    mutations: {
        SET_OBJECT_ID(state, payload) {
            if (typeof payload !== 'string') {
                console.log('payload is not a string');
                return;
            }
            state.object_id = payload;
        },

    },

    actions: {
        setObjectID({ commit }, payload) {
            commit('SET_OBJECT_ID', payload);
        },
    },
};
