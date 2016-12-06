// This is the js for the default/index.html view.

var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};

    self.get_user_data = function () {
        $.getJSON(get_user_data_url, function (data) {
            self.vue.user_data = data.user;
            self.vue.steps = data.steps;
            self.vue.user_data_present = data.user_data_present;
            self.vue.logged_in = data.logged_in;
            self.vue.fitbit_linked = data.fitbit_linked;
            self.vue.$nextTick(function() {
				self.draw_chart();
            });
        });

    };

    self.add_friend = function() {
      $.post(add_friend_url,
         {
           friend: $( "#find_friends" ).val()
         },
         function (data) {
           $("#find_friends").val('');
         }); 
    };

    self.accept_friend = function(email) {
      $.post(accept_friend_url,
         {
           friend: email
         },
         function (data) {
           self.get_friend_data()
         }); 
    };

    self.deny_friend = function(email) {
      $.post(deny_friend_url,
         {
           friend: email
         },
         function (data) {
           self.get_friend_data()
         }); 
    };

    self.compare_friend= function(friend) {
      self.vue.friend_week_avg_s = friend.weekly;
      self.vue.friend_today_s = friend.today;
      self.vue.friend_user_name = friend.user_name;
      self.vue.friend_first_name = friend.first_name;
      self.draw_my_friend_bar();
    };

    self.add_steps_data = function() {
      $.post(add_steps_data_url,
         {
           day: self.vue.input_day,
           steps: self.vue.input_steps
         },
         function (data) {
           self.get_user_data();
         }); 
    };

    self.get_friend_data = function() {
         $.getJSON(get_friend_data_url, function (data) {
           self.vue.friend_data = data.friend_data;
           self.vue.friend_requests = data.friend_requests;
           self.draw_my_friend_bar();
         }); 
    };

    self.add_user_data = function() {
        $.post(add_user_data_url,
            {
                dob: self.vue.input_dob,
                sex: self.vue.input_sex,
                height: self.vue.input_height,
                weight: self.vue.input_weight,
                image: self.vue.input_img,
                steps_target: self.vue.input_steps_target,
                weight_target: self.vue.input_weight_target
            },
            function (data) {
                self.vue.user_data = data.user;
                self.vue.logged_in = data.logged_in;
                self.vue.user_data_present = data.user_data_present;
                self.vue.input_dob = null;
                self.vue.input_sex = null;
                self.vue.input_height = null;
                self.vue.input_weight = null;
                self.vue.input_img = null;
                self.vue.input_steps_target = null;
                self.vue.input_weight_target = null;
                self.goto('activity');
            });
    };


    self.redirect_fitbit = function(){
    window.location.href=
    "https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=227XNF&redirect_uri=https%3A%2F%2Fnojha.pythonanywhere.com%2Fproject%2Fdefault%2Ffitbit_auth&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800"
    };

    self.draw_bar = function() {
        var data = [{
            x: self.vue.steps.weekdays,
            y: self.vue.steps.week_steps,
            type: 'bar'
        }];
        var layout = {
                        title: 'Weekly Steps',
                        displayModeBar: false,
                        autosize: false,
                        width: 450,
                        height: 450
                      };
        Plotly.newPlot('show-bar', data, layout);
    };

    self.draw_grouped_bar = function() {
        var trace1 = {
            x: ["Weight"],
            y: [self.vue.user_data.weight_target],
            type: 'bar',
            name: 'Target'
        };
        var trace2 = {
            x: ["Weight"],
            y: [self.vue.user_data.weight],
            type: 'bar',
            name: 'Current'
        };
        var data = [trace1, trace2];
        var layout = {
                        title: 'Weight', 
                        barmode: 'group',
                        displayModeBar: false,
                        autosize: false,
                        width: 350,
                        height: 450
                      };
        Plotly.newPlot('show-weight-bar', data, layout);
    };

    self.draw_my_friend_bar = function() {
        var trace1 = {
            x: ["Steps"],
            y: [self.vue.steps.today_s],
            type: 'bar',
            name: 'Self'
        };
        var trace2 = {
            x: ["Steps"],
            y: [self.vue.friend_today_s],
            type: 'bar',
            name: self.vue.friend_first_name
        };
        var data = [trace1, trace2];
        var layout = {
                        title: 'Steps Today', 
                        barmode: 'group',
                        displayModeBar: false,
                      };
        Plotly.newPlot('show-my-today-bar', data, layout);

        var trace3 = {
            x: ["Steps"],
            y: [self.vue.steps.week_avg_s],
            type: 'bar',
            name: 'Self'
        };
        var trace4 = {
            x: ["Steps"],
            y: [self.vue.friend_week_avg_s],
            type: 'bar',
            name: self.vue.friend_first_name
        };
        var data_w = [trace3, trace4];
        var layout_w = {
                        title: 'Steps for the week', 
                        barmode: 'group',
                        displayModeBar: false,
                      };
        Plotly.newPlot('show-my-week-bar', data_w, layout_w);
    };

    self.draw_chart = function(){
        label_daily =  "Target: " + self.vue.user_data.steps_target;
        percent_daily = Math.round((100 * self.vue.steps.today_s)/self.vue.user_data.steps_target);
        var rp1 = radialProgress(document.getElementById('daily_steps_radial'))
            .label(label_daily)
            .diameter(250)
            .value(percent_daily)
            .render();

        label_weekly = "Target: " + self.vue.user_data.steps_target;
        percent_weekly =  Math.round((100 * self.vue.steps.week_avg_s)/self.vue.user_data.steps_target);
        var rp2 = radialProgress(document.getElementById('weekly_steps_radial'))
            .label(label_weekly)
            .diameter(250)
            .value(percent_weekly)
            .render();

        self.draw_bar();
        self.draw_grouped_bar();
    };

    self.onFileChange = function(e) {
      var files = e.target.files || e.dataTransfer.files;
      if (!files.length)
        return;
      this.createImage(files[0]);
    };

    self.createImage = function(file) {
      var image = new Image();
      var reader = new FileReader();
      var vm = this;

      reader.onload = (e) => {
        vm.input_img = e.target.result;
      };
      reader.readAsDataURL(file);
    };

    self.removeImage = function (e) {
      this.input_img = '';
    };

    self.friend_autocomplete = function() {
      var cache = {};
      $( "#find_friends" ).autocomplete({
        minLength: 2,
        source: function( request, response ) {
          var term = request.term;
          if ( term in cache ) {
            response( cache[ term ] );
            return;
          }
 
          $.getJSON(get_user_list_url, request, function( data ) {
            cache[ term ] = data;
            response( data );
          });
        }
      });
    }

    self.goto = function (page) {
        self.vue.page = page;
        if (page == 'activity') {
            self.get_user_data();
        }
        if (page == 'edit_profile') {
            self.vue.input_dob = self.vue.user_data.dob;
            self.vue.input_sex = self.vue.user_data.sex;
            self.vue.input_height = self.vue.user_data.height;
            self.vue.input_weight = self.vue.user_data.weight;
            self.vue.input_img = self.vue.user_data.image;
            self.vue.input_steps_target = self.vue.user_data.steps_target;
            self.vue.input_weight_target = self.vue.user_data.weight_target;
        }
        if (page == 'friends') {
            self.get_friend_data();
	    self.vue.$nextTick(function() {
                self.friend_autocomplete();
            });
	}
    };

    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            logged_in: false,
            user_data_present: false,
            user_data: null,
            steps: null,
            input_dob: null,
            input_sex: null,
            input_height: null,
            input_weight: null,
            input_img : null,
            input_steps_target: null,
            input_weight_target: null,
            input_day: null,
            input_steps: null,
            data_available: false,
            page: "activity",
            fitbit_linked: false,
            friend_data: null,
            friend_requests: null,
            friend_week_avg_s: null,
            friend_today_s: null,
            friend_user_name: "",
            friend_first_name: "" 
        },
        methods: {
            add_user_data: self.add_user_data,
            redirect_fitbit: self.redirect_fitbit,
            onFileChange: self.onFileChange,
            createImage: self.createImage,
            removeImage: self.removeImage,
            goto: self.goto,
            get_user_data: self.get_user_data,
            add_steps_data: self.add_steps_data,
            add_friend: self.add_friend,
            accept_friend: self.accept_friend,
            deny_friend: self.deny_friend,
            compare_friend: self.compare_friend,
        },

        ready: function()
        {
            self.get_user_data();
        }

    });


    self.get_user_data();
    //self.draw_chart();
    $("#vue-div").show();



    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
