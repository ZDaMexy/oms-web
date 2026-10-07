// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the GNU Affero General Public License v3.0.
// See the LICENCE file in the repository root for full licence text.

'use strict';

const path = require('path');
const Autoprefixer = require('autoprefixer');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const dotenv = require('dotenv');
const ForkTsCheckerWebpackPlugin = require('fork-ts-checker-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');
const webpack = require('webpack');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');

const env = process.env.NODE_ENV || 'development';
dotenv.config({ path: `.env.${env}` });
dotenv.config();
const inProduction = env === 'production';
const resolvePath = (...segments) => path.resolve(__dirname, ...segments);
const outputFilename = (name, ext = '[ext]') => `${name}.[contenthash:8]${ext}`;

// Only implemented OMS pages enter the import graph. The original page entry
// names, manifest, loaders and shared chunks remain.
const entry = {
  app: [resolvePath('resources/css/entrypoints/app.less'), resolvePath('resources/js/entrypoints/app.ts')],
  beatmaps: resolvePath('resources/js/entrypoints/beatmaps.tsx'),
  'beatmapsets-show': resolvePath('resources/js/entrypoints/beatmapsets-show.tsx'),
  'profile-page': resolvePath('resources/js/entrypoints/profile-page.tsx'),
};
const plugins = [
  new ForkTsCheckerWebpackPlugin({ async: false, typescript: { memoryLimit: 256 } }),
  new webpack.ProvidePlugin({ $: 'jquery', _: 'lodash', jQuery: 'jquery', moment: 'moment', React: 'react', ReactDOM: 'react-dom' }),
  new webpack.IgnorePlugin({ contextRegExp: /moment$/, resourceRegExp: /^\.\/locale$/ }),
  new MiniCssExtractPlugin({ filename: outputFilename('css/[name]', '.css') }),
  new WebpackManifestPlugin({
    filter: (file) => /^\/assets\/(?:css|js)\/.*\.(?:css|js)$/.test(file.path),
    map: (file) => {
      const baseDir = file.path.match(/^\/assets\/(css|js)\//)?.[1];
      if (baseDir != null && !file.name.startsWith(`${baseDir}/`)) file.name = `${baseDir}/${file.name}`;
      return file;
    },
  }),
];
const rules = [
  { test: /\.tsx?$/, exclude: /node_modules/, loader: 'ts-loader', options: { transpileOnly: false } },
  { test: /\.coffee$/, use: ['coffee-loader'] },
  {
    test: /\.less$/,
    use: [
      MiniCssExtractPlugin.loader,
      { loader: 'css-loader', options: { importLoaders: 1, sourceMap: true } },
      { loader: 'postcss-loader', options: { postcssOptions: { plugins: [Autoprefixer] } } },
      { loader: 'less-loader', options: { sourceMap: true } },
    ],
  },
  { test: /(\.(png|jpe?g|gif|webp)$|^((?!font).)*\.svg$)/, type: 'asset/resource', generator: { filename: outputFilename('images/[name]') } },
  { test: /(\.(woff2?|ttf|eot|otf)$|font.*\.svg$)/, type: 'asset/resource', generator: { filename: outputFilename('fonts/[name]') } },
];
const optimization = {
  moduleIds: 'deterministic',
  runtimeChunk: { name: 'runtime' },
  splitChunks: {
    cacheGroups: {
      commons: { chunks: 'initial', minChunks: 2, name: 'commons', priority: -20 },
      vendor: {
        chunks: 'initial', name: 'vendor', priority: -10, reuseExistingChunk: true,
        test: (module) => module.resource && module.resource.includes(`${path.sep}node_modules${path.sep}`),
      },
    },
  },
};
if (inProduction) optimization.minimizer = [new TerserPlugin({ parallel: false }), new CssMinimizerPlugin({ parallel: false })];
module.exports = {
  mode: inProduction ? 'production' : 'development',
  devtool: inProduction ? false : 'source-map',
  entry,
  output: { filename: outputFilename('js/[name]', '.js'), path: resolvePath('public/assets'), publicPath: '/assets/' },
  plugins,
  module: { rules },
  resolve: {
    alias: { '@fonts': resolvePath('resources/fonts'), '@image_resources': resolvePath('resources/images'), '@images': resolvePath('public/images') },
    extensions: ['.js', '.coffee', '.ts', '.tsx'],
    modules: [resolvePath('resources/js'), 'node_modules'],
    plugins: [new TsconfigPathsPlugin()],
  },
  optimization,
};
