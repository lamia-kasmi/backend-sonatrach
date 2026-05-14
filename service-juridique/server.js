const dotenv = require('dotenv');
dotenv.config({ path: './config.env' });

const mongoose = require('mongoose');
const app      = require('./app');
const { startEureka, stopEureka } = require('./services/eurekaService');

const PORT = process.env.PORT || 8084;

mongoose
  .connect(process.env.MONGODB_URI)
  .then(() => {
    console.log('✅ MongoDB connected');

    const server = app.listen(PORT, () => {
      console.log(`\n🚀 service-juridique → port ${PORT}`);
      console.log(`\n📋 Routes:`);
      console.log(`   GET              /health`);
      console.log(`   GET              /info`);
      console.log(`   ───────────────────────────────────`);
      console.log(`   GET              /juridique/directions/organigramme`);
      console.log(`   GET              /juridique/directions`);
      console.log(`   GET              /juridique/directions/:id`);
      console.log(`   POST  [admin]    /juridique/directions`);
      console.log(`   PUT   [admin]    /juridique/directions/:id`);
      console.log(`   DELETE[admin]    /juridique/directions/:id`);
      console.log(`   ───────────────────────────────────`);
      console.log(`   GET              /juridique/departements`);
      console.log(`   GET              /juridique/departements/:id`);
      console.log(`   GET              /juridique/departements/direction/:directionId`);
      console.log(`   POST  [admin]    /juridique/departements`);
      console.log(`   PUT   [admin]    /juridique/departements/:id`);
      console.log(`   DELETE[admin]    /juridique/departements/:id`);
      startEureka();
    });

    process.on('SIGTERM', () => {
      stopEureka();
      server.close(() => mongoose.connection.close(false, () => process.exit(0)));
    });
  })
  .catch((err) => {
    console.error('❌ MongoDB error:', err.message);
    process.exit(1);
  });