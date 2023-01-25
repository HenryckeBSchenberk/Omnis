const dotenv = require('dotenv');
const path = require('path');

let envfile = '.env';
if (process.env.NODE_ENV) {
  envfile += `.${process.env.NODE_ENV}`;
}

// const result = dotenv.config({
//   silent: true,
//   path: path.resolve('../', envfile),
// });

dotenv.config({
  silent: true,
  path: path.resolve('../', envfile),
});

// optional: check for errors
// if (result.error) {
//   throw result.error;
// }

module.exports = {
  devServer: {
    watchOptions: {
      ignored: /node_modules/,
      aggregateTimeout: 300,
      poll: 1000,
    },
  },
  pwa: {
    name: 'Parallax',
    themeColor: '#0D1D2D',
    msTileColor: '#ffffff',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'white',
    appleMobileWebAppCache: 'yes',
    manifestOptions: {
      background_color: '#ffffff',
    },
  },

  pluginOptions: {
    apollo: {
      lintGQL: false,
    },
  },

  pages: {
    index: {
      // entry for the page
      entry: 'src/main.js',
      filename: 'index.html',
      title: 'Omnis',
    },
  },

  transpileDependencies: ['vuetify'],
};
