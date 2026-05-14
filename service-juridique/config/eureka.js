const { Eureka } = require('eureka-js-client');

const client = new Eureka({
  instance: {
    app: process.env.SERVICE_NAME || 'service-juridique',
    hostName: 'localhost',
    ipAddr: '127.0.0.1',
    port: {
      $: parseInt(process.env.PORT) || 8084,
      '@enabled': true,
    },
    vipAddress: process.env.SERVICE_NAME || 'service-juridique',
    dataCenterInfo: {
      '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
      name: 'MyOwn',
    },
    statusPageUrl: `http://localhost:${process.env.PORT || 8084}/info`,
    healthCheckUrl: `http://localhost:${process.env.PORT || 8084}/health`,
  },
  eureka: {
    host: process.env.EUREKA_HOST || 'localhost',
    port: parseInt(process.env.EUREKA_PORT) || 8761,
    servicePath: '/eureka/apps/',
    maxRetries: 10,
    requestRetryDelay: 2000,
  },
});

module.exports = client;
